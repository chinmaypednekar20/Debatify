import { useState, useEffect, useRef } from "react";
import { fetchCategories, fetchCategorySummary } from "../api";

export default function CategoriesPage() {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCat, setSelectedCat] = useState(null);
    const [catDetail, setCatDetail] = useState(null);
    const [detailLoading, setDetailLoading] = useState(false);
    const [expandedQ, setExpandedQ] = useState(null);
    const detailRef = useRef(null);

    useEffect(() => {
        fetchCategories()
            .then(setCategories)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const handleCatClick = async (name) => {
        if (selectedCat === name) {
            setSelectedCat(null);
            setCatDetail(null);
            setExpandedQ(null);
            return;
        }
        setSelectedCat(name);
        setExpandedQ(null);
        setDetailLoading(true);
        try {
            const data = await fetchCategorySummary(name);
            setCatDetail(data);
            // scroll to detail after short delay for render
            setTimeout(() => {
                detailRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 100);
        } catch (err) {
            console.error(err);
        } finally {
            setDetailLoading(false);
        }
    };

    return (
        <div className="categories-page">
            <h1>📂 Categories</h1>
            <p className="page-desc">
                All questions classified by topic. Click a category to explore its
                questions and summary.
            </p>

            {loading ? (
                <div className="loading">
                    <div className="spinner"></div> Loading categories...
                </div>
            ) : (
                <>
                    <div className="categories-grid">
                        {categories.map((cat) => (
                            <div
                                key={cat.category}
                                className="category-card"
                                onClick={() => handleCatClick(cat.category)}
                                style={{
                                    borderLeftColor:
                                        selectedCat === cat.category ? "#E87E24" : undefined,
                                    background:
                                        selectedCat === cat.category
                                            ? "rgba(232,126,36,0.05)"
                                            : undefined,
                                }}
                            >
                                <h3>{cat.category}</h3>
                                <p className="count">
                                    <strong>{cat.count}</strong> question
                                    {cat.count !== 1 ? "s" : ""}
                                </p>
                            </div>
                        ))}
                    </div>

                    {selectedCat && (
                        <div className="category-detail" ref={detailRef}>
                            <h2>{selectedCat}</h2>
                            {detailLoading ? (
                                <div className="loading">
                                    <div className="spinner"></div> Loading...
                                </div>
                            ) : catDetail ? (
                                <>
                                    <p style={{ color: "#6c757d", marginBottom: "0.5rem" }}>
                                        {catDetail.count} question{catDetail.count !== 1 ? "s" : ""} in this category
                                    </p>
                                    <div className="combined">
                                        {catDetail.combined_summary}
                                    </div>

                                    <div className="questions-in-cat">
                                        <h4>Questions in this Category</h4>
                                        <div className="questions-list">
                                            {(catDetail.questions || []).filter(
                                                (q) =>
                                                    q.question_summary?.trim() ||
                                                    q.answer_summary?.trim() ||
                                                    q.overall_summary?.trim() ||
                                                    q.question_about?.trim()
                                            ).map((q, i) => (
                                                <div key={q.id || i} className="question-item">
                                                    <div
                                                        className="question-header"
                                                        onClick={() =>
                                                            setExpandedQ(expandedQ === i ? null : i)
                                                        }
                                                    >
                                                        <div className="q-icon">Q</div>
                                                        <div className="q-text">
                                                            {q.question_summary || q.question_about || "Question"}
                                                        </div>
                                                        <span
                                                            className={`chevron${expandedQ === i ? " open" : ""}`}
                                                        >
                                                            ▼
                                                        </span>
                                                    </div>
                                                    {expandedQ === i && (
                                                        <div className="question-body">
                                                            <div className="meta">
                                                                {q.ministry && (
                                                                    <span className="meta-tag ministry">
                                                                        {q.ministry}
                                                                    </span>
                                                                )}
                                                                {q.asked_by && (
                                                                    <span className="meta-tag askedby">
                                                                        Asked by: {q.asked_by}
                                                                    </span>
                                                                )}
                                                            </div>
                                                            {q.answer_summary && (
                                                                <>
                                                                    <div className="section-title">
                                                                        Answer
                                                                    </div>
                                                                    <p className="section-text">
                                                                        {q.answer_summary}
                                                                    </p>
                                                                </>
                                                            )}
                                                            {q.overall_summary && (
                                                                <>
                                                                    <div className="section-title">
                                                                        Summary
                                                                    </div>
                                                                    <p className="section-text">
                                                                        {q.overall_summary}
                                                                    </p>
                                                                </>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </>
                            ) : null}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
