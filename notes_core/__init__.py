"""
Notes Core Module - Centralized functionality for notes management, indexing, and querying.
"""

import json
import faiss
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import config from parent directory
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import DB_URL, MODEL_NAME, EMBEDDING_DIM, FAISS_INDEX_PATH, NOTES_JSON_PATH

Base = declarative_base()

class Note(Base):
    """Database model for notes."""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing integer ID
    title = Column(String(255))
    content = Column(Text)
    embedding = Column(Text)  # Store embedding as JSON string
    created = Column(DateTime)
    updated = Column(DateTime)


class NotesCore:
    """Core functionality for notes management, indexing, and querying."""
    
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.engine = create_engine(DB_URL)
        self.Session = sessionmaker(bind=self.engine)
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database and tables exist."""
        Base.metadata.create_all(self.engine)
    
    def load_notes_to_db(self) -> None:
        """Load notes from JSON file and store them in the database."""
        if not Path(NOTES_JSON_PATH).exists():
            print(f"No notes file found at {NOTES_JSON_PATH}")
            return

        session = self.Session()
        try:
            with open(NOTES_JSON_PATH, 'r') as f:
                notes = json.load(f)

            current_time = datetime.utcnow()
            for note_data in notes:
                # Create new note (ID will be auto-generated)
                note = Note(
                    title=note_data['title'],
                    content=note_data['content'],
                    embedding='',  # Embedding will be added by build_index
                    created=current_time,
                    updated=current_time
                )
                session.add(note)

            session.commit()
            print(f"Successfully loaded {len(notes)} notes into database")
        except Exception as e:
            session.rollback()
            print(f"Error loading notes: {e}")
        finally:
            session.close()
    
    def build_index(self) -> None:
        """Build FAISS index from notes in the database."""
        session = self.Session()

        try:
            # Get all notes
            notes = session.query(Note).all()
            
            if not notes:
                print("No notes found in database. Please run load_notes_to_db first.")
                return

            # Create FAISS index
            index = faiss.IndexFlatL2(EMBEDDING_DIM)
            note_ids = []
            embeddings = []
            
            # Process each note
            for note in notes:
                # Generate embedding
                embedding = self.model.encode(note.content)
                embeddings.append(embedding)
                note_ids.append(note.id)
                # Store embedding in database
                note.embedding = json.dumps(embedding.tolist())
            
            # Save changes to database
            session.commit()
            
            # Add to FAISS index
            index.add(np.array(embeddings, dtype=np.float32))
            
            # Save FAISS index and note IDs mapping
            faiss.write_index(index, FAISS_INDEX_PATH)
            with open("faiss_ids.json", "w") as f:
                json.dump(note_ids, f)
                
            print(f"Successfully built index for {len(notes)} notes")
            
        except Exception as e:
            session.rollback()
            print(f"Error building index: {e}")
        finally:
            session.close()
    
    def search_notes(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search notes using FAISS index and return top k results."""
        # Load index and note IDs
        index = self._load_index()
        note_ids = self._load_note_ids()
        
        # Generate embedding for the query
        query_embedding = self.model.encode(query)
        
        # Search in FAISS index
        distances, indices = index.search(
            np.array([query_embedding], dtype=np.float32), k
        )
        
        # Get notes from database
        session = self.Session()
        try:
            results = []
            for idx in indices[0]:
                if idx >= 0 and idx < len(note_ids):  # FAISS returns -1 for empty indices
                    note_id = note_ids[idx]
                    note = session.query(Note).get(note_id)
                    if note:
                        results.append({
                            'id': note.id,
                            'title': note.title,
                            'content': note.content
                        })
            return results
        finally:
            session.close()
    
    def format_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        formatted = f"Query: {query}\n\nRelevant Notes:\n"
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. {result['title']}\n"
            formatted += f"Content: {result['content']}\n"
        return formatted
    
    def _load_index(self):
        """Load the FAISS index from disk."""
        if not Path(FAISS_INDEX_PATH).exists():
            raise FileNotFoundError(
                f"No FAISS index found at {FAISS_INDEX_PATH}. "
                "Please run build_index first."
            )
        return faiss.read_index(FAISS_INDEX_PATH)
    
    def _load_note_ids(self):
        """Load the FAISS to DB note ID mapping."""
        id_path = Path("faiss_ids.json")
        if not id_path.exists():
            raise FileNotFoundError(
                "Missing faiss_ids.json. Please run build_index to generate it."
            )
        with open(id_path, "r") as f:
            return json.load(f) 