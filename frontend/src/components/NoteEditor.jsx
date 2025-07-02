import { useState, useEffect } from 'react'

function NoteEditor({ note, onUpdate, onDelete }) {
    const [title, setTitle] = useState(note.title);
    const [content, setContent] = useState(note.content);

    useEffect(() => {
        setTitle(note.title);
        setContent(note.content);
    }, [note]);

    // Debounced auto-save
    useEffect(() => {
        const handler = setTimeout(() => {
            if (title !== note.title || content !== note.content) {
                onUpdate({ ...note, title, content });
            }
        }, 500); // 500ms debounce
        return () => clearTimeout(handler);
    }, [title, content, note, onUpdate]);

    return (
        <div className="note-editor" style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '1rem' }}>
            <input
                value={title}
                onChange={e => setTitle(e.target.value)}
                style={{
                    fontSize: '1.3em',
                    fontWeight: 'bold',
                    marginBottom: '1rem',
                    padding: '0.5em',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    width: '100%',
                    maxWidth: '900px',
                }}
                placeholder="Title"
            />
            <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                style={{
                    flex: 1,
                    minHeight: '400px',
                    resize: 'vertical',
                    fontSize: '1.1em',
                    padding: '1em',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    width: '100%',
                    maxWidth: '900px',
                }}
                placeholder="Start writing your note..."
            />
        </div>
    );
}

export default NoteEditor