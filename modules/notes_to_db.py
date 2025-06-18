import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_URL, NOTES_JSON_PATH

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    embedding = Column(Text)  # Store embedding as JSON string
    created = Column(DateTime)
    updated = Column(DateTime)

def load_notes_to_db():
    """Load notes from JSON file and store them in the database."""
    if not Path(NOTES_JSON_PATH).exists():
        print(f"No notes file found at {NOTES_JSON_PATH}")
        return

    # Initialize database
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with open(NOTES_JSON_PATH, 'r') as f:
            notes = json.load(f)

        current_time = datetime.utcnow()
        for note_data in notes:
            # Create new note
            note = Note(
                title=note_data['title'],
                content=note_data['content'],
                embedding='',  # Embedding will be added by build_index.py
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

if __name__ == "__main__":
    load_notes_to_db() 