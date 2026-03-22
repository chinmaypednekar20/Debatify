import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchDebate, chatWithDebate } from "../api";

function formatDate(d) {
    return new Date(d).toLocaleDateString("en-US", {
        year: "numeric", month: "long", day: "numeric",
    });
}

function FormattedText({ text }) {
    if (!text) return null;
    return (
        <div style={{ textAlign: "justify", lineHeight: "1.6" }}>
            {text.split(/\n+/).map((paragraph, idx) => {
                if (!paragraph.trim()) return null;
                const parts = paragraph.split(/(\*\*.*?\*\*|\*.*?\*)/g);
                return (
                    <p key={idx} style={{ marginBottom: "1rem" }}>
                        {parts.map((part, i) => {
                            if (part.startsWith("**") && part.endsWith("**")) {
                                return <strong key={i} style={{ fontWeight: "bold" }}>{part.slice(2, -2)}</strong>;
                            }
                            if (part.startsWith("*") && part.endsWith("*")) {
                                return <em key={i}>{part.slice(1, -1)}</em>;
                            }
                            return part;
                        })}
                    </p>
                );
            })}
        </div>
    );
}


export default function DebatePage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [debate, setDebate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("questions");
    const [openQuestion, setOpenQuestion] = useState(null);

    // Chat state
    const [messages, setMessages] = useState([
        {
            role: "assistant",
            text: "Hi! I can answer questions about this debate. What would you like to know?",
        },
    ]);
    const [input, setInput] = useState("");
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    useEffect(() => {
        fetchDebate(id)
            .then(setDebate)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [id]);

    // Auto-scroll to latest chat message
    useEffect(() => {
        if (activeTab === "chat") {
            chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, activeTab]);

    const handleSend = async () => {
        const question = input.trim();
        if (!question || chatLoading) return;

        setInput("");
        setMessages((prev) => [...prev, { role: "user", text: question }]);
        setChatLoading(true);

        try {
            const data = await chatWithDebate(id, question);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: data.answer },
            ]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: "Sorry, I couldn't get an answer right now. Please make sure Ollama is running.",
                },
            ]);
        } finally {
            setChatLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (loading)
        return (
            <div className="loading">
                <div className="spinner"></div> Loading debate...
            </div>
        );
    if (!debate)
        return <div className="loading">Debate not found.</div>;

    const questions = debate.questions || [];

    return (
        <div className="debate-detail">
            <button className="back-btn" onClick={() => navigate(-1)}>
                ← Back to Debates
            </button>

            {/* Header */}
            <div className="debate-header">
                <div className="date-label">{formatDate(debate.date)}</div>
                <h1>{debate.title}</h1>
                <FormattedText text={debate.overall_summary} />

                <div className="debate-stats">
                    <div className="stat-item">
                        <div className="stat-icon">❓</div>
                        <div>
                            <div className="label">Total Questions</div>
                            <div className="value">{questions.length}</div>
                        </div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-icon">🏛️</div>
                        <div>
                            <div className="label">Ministries</div>
                            <div className="value">
                                {new Set(questions.map((q) => q.ministry).filter(Boolean)).size}
                            </div>
                        </div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-icon">📂</div>
                        <div>
                            <div className="label">Categories</div>
                            <div className="value">
                                {new Set(questions.map((q) => q.category).filter(Boolean)).size}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
                <div
                    className={`tab${activeTab === "questions" ? " active" : ""}`}
                    onClick={() => setActiveTab("questions")}
                >
                    💬 Questions
                </div>
                <div
                    className={`tab${activeTab === "summary" ? " active" : ""}`}
                    onClick={() => setActiveTab("summary")}
                >
                    📝 Full Summary
                </div>
                <div
                    className={`tab${activeTab === "chat" ? " active" : ""}`}
                    onClick={() => setActiveTab("chat")}
                >
                    🤖 Ask AI
                </div>
            </div>

            {/* Tab content — Questions */}
            {activeTab === "questions" && (
                <div className="questions-list">
                    {questions.length === 0 ? (
                        <div className="loading" style={{ padding: "2rem" }}>
                            No questions found.
                        </div>
                    ) : (
                        questions.map((q) => (
                            <div key={q.id} className="question-item">
                                <div
                                    className="question-header"
                                    onClick={() =>
                                        setOpenQuestion(openQuestion === q.id ? null : q.id)
                                    }
                                >
                                    <div className="q-icon">Q</div>
                                    <div className="q-text">
                                        {q.question_summary || "Question"}
                                    </div>
                                    <span
                                        className={`chevron${openQuestion === q.id ? " open" : ""}`}
                                    >
                                        ▼
                                    </span>
                                </div>
                                {openQuestion === q.id && (
                                    <div className="question-body">
                                        <div className="meta">
                                            {q.ministry && (
                                                <span className="meta-tag ministry">{q.ministry}</span>
                                            )}
                                            {q.asked_by && (
                                                <span className="meta-tag askedby">
                                                    Asked by: {q.asked_by}
                                                </span>
                                            )}
                                            {q.category && (
                                                <span className="meta-tag category">{q.category}</span>
                                            )}
                                        </div>

                                        {q.answer_summary && (
                                            <>
                                                <div className="section-title">Answer Summary</div>
                                                <p className="section-text">{q.answer_summary}</p>
                                            </>
                                        )}

                                        {q.overall_summary && (
                                            <>
                                                <div className="section-title">Overall Summary</div>
                                                <p className="section-text">{q.overall_summary}</p>
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Tab content — Full Summary */}
            {activeTab === "summary" && (
                <div className="summary-box">
                    <h2>Complete Debate Summary</h2>
                    <FormattedText text={debate.overall_summary} />

                    <h2 style={{ marginTop: "2rem" }}>All Question Summaries</h2>
                    {questions.map((q, i) => (
                        <div key={q.id} style={{ marginTop: "1rem" }}>
                            <strong>
                                {i + 1}. {q.category || "Uncategorized"}
                            </strong>
                            <p style={{ color: "#6c757d", fontSize: "0.9rem", lineHeight: 1.6 }}>
                                {q.overall_summary}
                            </p>
                        </div>
                    ))}
                </div>
            )}

            {/* Tab content — AI Chat */}
            {activeTab === "chat" && (
                <div className="chat-container">
                    <div className="chat-header-info">
                        <span className="chat-badge">🤖 AI Debate Assistant</span>
                        <p className="chat-scope-note">
                            Answers are based only on this debate's summary content.
                        </p>
                    </div>

                    <div className="chat-history">
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`chat-bubble ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}
                            >
                                <div className="bubble-label">
                                    {msg.role === "user" ? "You" : "🤖 AI"}
                                </div>
                                <div className="bubble-text">{msg.text}</div>
                            </div>
                        ))}
                        {chatLoading && (
                            <div className="chat-bubble chat-assistant">
                                <div className="bubble-label">🤖 AI</div>
                                <div className="bubble-text chat-typing">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>

                    <div className="chat-input-area">
                        <textarea
                            className="chat-input"
                            rows={2}
                            placeholder="Ask a question about this debate…"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={chatLoading}
                        />
                        <button
                            className="chat-send-btn"
                            onClick={handleSend}
                            disabled={chatLoading || !input.trim()}
                        >
                            {chatLoading ? "…" : "Send ➤"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
