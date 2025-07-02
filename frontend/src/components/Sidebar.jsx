function Sidebar({ notes, currentNoteId, onSelect, onCreateNote, onDeleteNote }) {
    return (
        <div className="sidebar">
            <button onClick={onCreateNote}>+ New Note</button>
            <ul>
                {notes.map(note => (
                    <li
                        key={note.id}
                        style={{ display: 'flex', alignItems: 'center', fontWeight: note.id === currentNoteId ? 'bold' : 'normal' }}
                    >
                        <span style={{ flex: 1, cursor: 'pointer' }} onClick={() => onSelect(note.id)}>
                            {note.title}
                        </span>
                        <button
                            style={{ marginLeft: '0.5em', background: 'none', border: 'none', cursor: 'pointer', color: '#c00', fontSize: '1.2em', lineHeight: '1' }}
                            title="Delete note"
                            onClick={e => { e.stopPropagation(); onDeleteNote(note.id); }}
                        >
                            ×
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Sidebar