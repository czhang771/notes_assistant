import { useState, useEffect } from 'react'
import { fetchNotes, createNote, updateNote, deleteNote, askQuestion } from './api/notes'
import Sidebar from './components/Sidebar'
import NoteEditor from './components/NoteEditor'
import AskBar from './components/AskBar'
import './App.css'

function App() {
  const [notes, setNotes] = useState([])
  const [currentNoteId, setCurrentNoteId] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [references, setReferences] = useState([])

  useEffect(() => {
    fetchNotes().then(setNotes)
  }, [])

  const currentNote = notes.find(note => note.id === currentNoteId)

  console.log('notes:', notes, 'currentNoteId:', currentNoteId, 'currentNote:', currentNote)

  async function handleCreateNote() {
    console.log('Creating new note...')
    const newNote = await createNote('Untitled Note', '')
    setNotes(prev => [...prev, newNote])
    setCurrentNoteId(newNote.id)
  }

  async function handleUpdateNote(updatedNote) {
    const saved = await updateNote(updatedNote.id, {
      title: updatedNote.title,
      content: updatedNote.content,
    });
    setNotes(prev => prev.map(note => (note.id === saved.id ? saved : note)));
  }

  async function handleDeleteNote(id) {
    await deleteNote(id);
    setNotes(prev => prev.filter(note => note.id !== id));
    setCurrentNoteId(null);
  }

  async function handleAskQuestion(question) {
    const result = await askQuestion(question);
    setAnswer(result.answer);
    setReferences(result.references || []);
  }

  return (
    <div className="app" style={{ display: 'flex', flexDirection: 'row', height: '100vh' }}>
      <div style={{ width: '260px', minWidth: '200px', borderRight: '1px solid #eee', background: '#fafbfc', height: '100vh', boxSizing: 'border-box' }}>
        <Sidebar
          notes={notes}
          currentNoteId={currentNoteId}
          onSelect={setCurrentNoteId}
          onCreateNote={handleCreateNote}
          onDeleteNote={handleDeleteNote}
        />
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {currentNote ? (
          <NoteEditor
            note={currentNote}
            onUpdate={handleUpdateNote}
            onDelete={() => handleDeleteNote(currentNote.id)}
          />
        ) : (
          <div style={{ padding: "2rem" }}>Select or create a note to get started.</div>
        )}
        <AskBar
          onAsk={handleAskQuestion}
          answer={answer}
          references={references}
        />
      </div>
    </div>
  )
}

export default App
