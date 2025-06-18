"""
FastAPI application that wraps NotesCore functionality for frontend integration.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add parent directory to path to import notes_core
sys.path.append(str(Path(__file__).parent))
from notes_core import NotesCore, Note as NoteModel

# Global NotesCore instance
notes_core = NotesCore()

# Pydantic models for request/response validation
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(NoteBase):
    id: int
    created: datetime
    updated: datetime

    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    references: List[NoteResponse]

class DeleteResponse(BaseModel):
    message: str
    deleted_note_id: int

# FastAPI app with CORS for frontend integration
app = FastAPI(
    title="Notes Assistant API",
    description="API for managing and querying notes with semantic search",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    """Create a new note."""
    try:
        session = notes_core.Session()
        
        # Create new note with auto-generated ID
        new_note = NoteModel(
            title=note.title,
            content=note.content,
            embedding='',  # Will be populated when index is rebuilt
            created=datetime.utcnow(),
            updated=datetime.utcnow()
        )
        
        session.add(new_note)
        session.commit()
        session.refresh(new_note)
        
        # Convert to response model
        response_note = NoteResponse(
            id=new_note.id,
            title=new_note.title,
            content=new_note.content,
            created=new_note.created,
            updated=new_note.updated
        )
        
        session.close()
        return response_note
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")

@app.get("/notes", response_model=List[NoteResponse])
async def get_all_notes():
    """Get all notes."""
    try:
        session = notes_core.Session()
        notes = session.query(NoteModel).all()
        
        response_notes = []
        for note in notes:
            response_notes.append(NoteResponse(
                id=note.id,
                title=note.title,
                content=note.content,
                created=note.created,
                updated=note.updated
            ))
        
        session.close()
        return response_notes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notes: {str(e)}")

@app.patch("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_update: NoteUpdate):
    """Update an existing note."""
    try:
        session = notes_core.Session()
        
        # Find the note
        note = session.query(NoteModel).filter(NoteModel.id == note_id).first()
        if not note:
            session.close()
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update fields if provided
        if note_update.title is not None:
            note.title = note_update.title
        if note_update.content is not None:
            note.content = note_update.content
        
        # Update timestamp and clear embedding (will be regenerated when index is rebuilt)
        note.updated = datetime.utcnow()
        note.embedding = ''
        
        session.commit()
        session.refresh(note)
        
        # Convert to response model
        response_note = NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            created=note.created,
            updated=note.updated
        )
        
        session.close()
        return response_note
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")

@app.delete("/notes/{note_id}", response_model=DeleteResponse)
async def delete_note(note_id: int):
    """Delete a note by ID."""
    try:
        session = notes_core.Session()
        
        # Find the note
        note = session.query(NoteModel).filter(NoteModel.id == note_id).first()
        if not note:
            session.close()
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Store the ID for response
        deleted_id = note.id
        
        # Delete the note
        session.delete(note)
        session.commit()
        
        session.close()
        
        return DeleteResponse(
            message="Note deleted successfully",
            deleted_note_id=deleted_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_notes(query_request: QueryRequest):
    """Query notes using semantic search and return answer with references."""
    try:
        # Search for relevant notes
        results = notes_core.search_notes(query_request.question, k=query_request.k)
        
        if not results:
            return QueryResponse(
                answer="No relevant notes found for your question.",
                references=[]
            )
        
        # Convert results to NoteResponse objects
        references = []
        for result in results:
            references.append(NoteResponse(
                id=result['id'],
                title=result['title'],
                content=result['content'],
                created=datetime.utcnow(),  # We don't have these in search results
                updated=datetime.utcnow()
            ))
        
        # Format the answer using the existing format_results method
        formatted_results = notes_core.format_results(query_request.question, results)
        
        return QueryResponse(
            answer=formatted_results,
            references=references
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying notes: {str(e)}")

@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the semantic search index after notes have been modified."""
    try:
        notes_core.build_index()
        return {"message": "Index rebuilt successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding index: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Notes Assistant API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 