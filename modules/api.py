from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class NoteDB(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(Text)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response
class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(NoteBase):
    id: int
    created: datetime
    updated: datetime

    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(title="Notes API")

@app.post("/notes/", response_model=Note)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = NoteDB(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/notes/", response_model=List[Note])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(NoteDB).offset(skip).limit(limit).all()
    return notes

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db_note.updated = datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 