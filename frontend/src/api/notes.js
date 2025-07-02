const BASE_URL = "http://127.0.0.1:8000";

export async function fetchNotes() {
    const response = await fetch(`${BASE_URL}/notes`);
    return response.json();
}

export async function createNote(title, content) {
    const response = await fetch(`${BASE_URL}/notes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, content }),
    });
    return response.json();
}

export async function updateNote(id, data) {
    const response = await fetch(`${BASE_URL}/notes/${id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
    return response.json();
}

export async function deleteNote(id) {
    const res = await fetch(`${BASE_URL}/notes/${id}`, {
        method: 'DELETE'
    });
    return await res.json();
}

export async function askQuestion(question) {
    // First, rebuild the index
    await fetch(`${BASE_URL}/rebuild-index`, {
        method: "POST"
    });
    // Then, send the query
    const response = await fetch(`${BASE_URL}/query`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
    });
    return response.json();
}
