import { useState, useEffect } from "react";
import { fetchOverallSummary } from "../api";

export default function OverallSummaryPage() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchOverallSummary()
            .then(setData)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    if (loading)
        return (
            <div className="loading">
                <div className="spinner"></div> Loading overall summary...
            </div>
        );

    if (!data) return <div className="loading">No data available.</div>;

    return (
        <div className="overall-summary-page">
            <h1>📊 Session Overview</h1>
            <p className="page-desc">
                A high-level summary of all questions raised during this parliamentary
                session.
            </p>

            {/* Stats */}
            <div className="summary-stats">
                <div className="summary-stat-card">
                    <div className="big-num">{data.total_questions}</div>
                    <div className="stat-label">Questions Raised</div>
                </div>
                <div className="summary-stat-card">
                    <div className="big-num">{data.total_categories}</div>
                    <div className="stat-label">Topic Categories</div>
                </div>
                <div className="summary-stat-card">
                    <div className="big-num">{data.total_ministries}</div>
                    <div className="stat-label">Ministries Addressed</div>
                </div>
            </div>

            {/* Executive summary */}
            <div className="summary-box">
                <h2>📝 Executive Summary</h2>
                <p>{data.combined_summary}</p>
            </div>

            {/* Top ministries */}
            {data.top_ministries && data.top_ministries.length > 0 && (
                <div className="summary-box">
                    <h2>🏛️ Most Questioned Ministries</h2>
                    <div className="ministry-bars">
                        {data.top_ministries.map((m) => (
                            <div key={m.name} className="ministry-bar-row">
                                <span className="ministry-name">{m.name}</span>
                                <div className="bar-track">
                                    <div
                                        className="bar-fill"
                                        style={{
                                            width: `${Math.max(
                                                8,
                                                (m.count / data.top_ministries[0].count) * 100
                                            )}%`,
                                        }}
                                    ></div>
                                </div>
                                <span className="bar-count">{m.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Category breakdown */}
            <div className="summary-box">
                <h2>📂 Category Breakdown</h2>
                <ul className="breakdown-list">
                    {data.category_breakdown.map((cat) => (
                        <li key={cat.category} className="breakdown-item">
                            <span className="cat-badge">{cat.count}</span>
                            <div className="cat-info">
                                <h4>{cat.category}</h4>
                                <p>{cat.summary}</p>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
