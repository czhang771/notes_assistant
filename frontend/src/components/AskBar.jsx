import { useState } from 'react'

function AskBar({ onAsk, answer, references }) {
    const [question, setQuestion] = useState('');
    const [lastQuery, setLastQuery] = useState('');

    function handleSubmit(e) {
        e.preventDefault();
        onAsk(question);
        setLastQuery(question);
        setQuestion('');
    }

    return (
        <div className="ask-bar" style={{ marginTop: '2rem', padding: '1rem', background: '#f7f7fa', borderRadius: '8px' }}>
            <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                    placeholder="Ask your notes anything..."
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    style={{ flex: 1, padding: '0.5em', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <button type="submit" style={{ padding: '0.5em 1em' }}>Ask</button>
            </form>
            {lastQuery && (
                <div style={{ marginTop: '1.5rem' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '0.5em' }}>Query:</div>
                    <div style={{ marginBottom: '1em', fontStyle: 'italic', color: '#333' }}>{lastQuery}</div>
                    {references && references.length > 0 && (
                        <div>
                            <div style={{ fontWeight: 'bold', marginBottom: '0.5em' }}>Relevant Notes:</div>
                            <ul style={{ paddingLeft: '1.2em' }}>
                                {references.map(ref => (
                                    <li key={ref.id} style={{ marginBottom: '0.5em' }}>
                                        <span style={{ fontWeight: 'bold' }}>{ref.title}</span>
                                        <div style={{ fontSize: '0.95em', color: '#555' }}>
                                            {ref.content.length > 120 ? ref.content.slice(0, 120) + '...' : ref.content}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default AskBar