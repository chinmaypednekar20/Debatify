import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { fetchDebates, fetchDates } from "../api";

const DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

function formatDate(d) {
    return new Date(d).toLocaleDateString("en-US", {
        year: "numeric", month: "long", day: "numeric",
    });
}

export default function HomePage() {
    const navigate = useNavigate();
    const today = new Date();

    const [currentMonth, setCurrentMonth] = useState(today.getMonth());
    const [currentYear, setCurrentYear] = useState(today.getFullYear());
    const [selectedDate, setSelectedDate] = useState(null);
    const [debates, setDebates] = useState([]);
    const [availableDates, setAvailableDates] = useState([]);
    const [loading, setLoading] = useState(true);

    // Load available dates
    useEffect(() => {
        fetchDates().then(setAvailableDates).catch(console.error);
    }, []);

    // Load debates
    useEffect(() => {
        setLoading(true);
        fetchDebates(selectedDate)
            .then(setDebates)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [selectedDate]);

    // Calendar helpers
    const calendarDays = useMemo(() => {
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();
        const cells = [];

        // Previous month padding
        for (let i = firstDay - 1; i >= 0; i--) {
            cells.push({ day: daysInPrevMonth - i, otherMonth: true });
        }
        // Current month days
        for (let d = 1; d <= daysInMonth; d++) {
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
            cells.push({
                day: d,
                dateStr,
                isToday:
                    d === today.getDate() &&
                    currentMonth === today.getMonth() &&
                    currentYear === today.getFullYear(),
                hasData: availableDates.includes(dateStr),
                isSelected: selectedDate === dateStr,
            });
        }
        // Next month padding
        const remaining = 7 - (cells.length % 7);
        if (remaining < 7) {
            for (let i = 1; i <= remaining; i++) {
                cells.push({ day: i, otherMonth: true });
            }
        }
        return cells;
    }, [currentMonth, currentYear, availableDates, selectedDate]);

    const handleDayClick = (cell) => {
        if (cell.otherMonth) return;
        if (selectedDate === cell.dateStr) {
            setSelectedDate(null); // toggle off
        } else {
            setSelectedDate(cell.dateStr);
        }
    };

    const prevMonth = () => {
        if (currentMonth === 0) {
            setCurrentMonth(11);
            setCurrentYear(currentYear - 1);
        } else {
            setCurrentMonth(currentMonth - 1);
        }
    };

    const nextMonth = () => {
        if (currentMonth === 11) {
            setCurrentMonth(0);
            setCurrentYear(currentYear + 1);
        } else {
            setCurrentMonth(currentMonth + 1);
        }
    };

    return (
        <>
            {/* Hero */}
            <section className="hero">
                <h1>
                    Democracy, <span>Summarized.</span>
                </h1>
                <p>
                    Explore concise summaries of Indian Parliament debates. Select a date
                    to dive into the proceedings, bills passed, and key discussions.
                </p>
            </section>

            {/* Main grid */}
            <div className="main-content">
                {/* Calendar */}
                <div className="calendar-card">
                    <h3>📅 Select a Date</h3>
                    <p className="subtitle">Dates with dots have records</p>

                    <div className="calendar-nav">
                        <button onClick={prevMonth}>‹</button>
                        <span className="month-label">
                            {MONTHS[currentMonth]} {currentYear}
                        </span>
                        <button onClick={nextMonth}>›</button>
                    </div>

                    <div className="calendar-grid">
                        {DAYS.map((d) => (
                            <div key={d} className="day-header">{d}</div>
                        ))}
                        {calendarDays.map((cell, i) => (
                            <div
                                key={i}
                                className={`day${cell.otherMonth ? " other-month" : ""}${cell.isToday ? " today" : ""}${cell.isSelected ? " selected" : ""}${cell.hasData ? " has-data" : ""}`}
                                onClick={() => handleDayClick(cell)}
                            >
                                {cell.day}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Proceedings */}
                <div className="proceedings-section">
                    <h2>
                        {selectedDate
                            ? `Proceedings for ${formatDate(selectedDate)}`
                            : "Latest Proceedings"}
                    </h2>

                    {loading ? (
                        <div className="loading">
                            <div className="spinner"></div> Loading debates...
                        </div>
                    ) : debates.length === 0 ? (
                        <div className="loading" style={{ color: "#adb5bd" }}>
                            No debates found{selectedDate ? " for this date" : ""}.
                        </div>
                    ) : (
                        debates.map((d) => (
                            <div
                                key={d.id}
                                className="debate-card"
                                onClick={() => navigate(`/debate/${d.id}`)}
                            >
                                <div className="date-label">{formatDate(d.date)}</div>
                                <h3>{d.title}</h3>
                                <p>{d.overall_summary}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </>
    );
}
