const API_BASE = "http://localhost:8000/api";

function getHeaders() {
    const token = localStorage.getItem("token");
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    return headers;
}

export async function signup(username, email, password) {
    const res = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Signup failed");
    }
    return res.json();
}

export async function login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Login failed");
    }
    return res.json();
}

export async function fetchDebates(date = null) {
    const url = date ? `${API_BASE}/debates?date=${date}` : `${API_BASE}/debates`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
}

export async function fetchDebate(id) {
    const res = await fetch(`${API_BASE}/debates/${id}`, { headers: getHeaders() });
    return res.json();
}

export async function fetchDates() {
    const res = await fetch(`${API_BASE}/dates`, { headers: getHeaders() });
    return res.json();
}

export async function fetchCategories() {
    const res = await fetch(`${API_BASE}/categories`, { headers: getHeaders() });
    return res.json();
}

export async function fetchCategorySummary(name) {
    const res = await fetch(`${API_BASE}/categories/${encodeURIComponent(name)}/summary`, {
        headers: getHeaders(),
    });
    return res.json();
}

export async function fetchOverallSummary() {
    const res = await fetch(`${API_BASE}/overall-summary`, { headers: getHeaders() });
    return res.json();
}

export async function chatWithDebate(summaryId, question) {
    const res = await fetch(`${API_BASE}/summaries/${summaryId}/chat`, {
        method: "POST",
        headers: { ...getHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Chat request failed");
    }
    return res.json(); // { answer: "..." }
}
