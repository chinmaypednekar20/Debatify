import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
    const location = useLocation();
    const navigate = useNavigate();
    const user = localStorage.getItem("username");

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
        navigate("/login");
    };

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                <div className="logo-icon">DB</div>
                <div>
                    Debatify
                    <small>Indian Parliamentary Debates</small>
                </div>
            </Link>
            <div className="navbar-links">
                <Link to="/" className={location.pathname === "/" ? "active" : ""}>
                    Home
                </Link>
                <Link
                    to="/categories"
                    className={location.pathname === "/categories" ? "active" : ""}
                >
                    Categories
                </Link>
                <Link
                    to="/overall-summary"
                    className={location.pathname === "/overall-summary" ? "active" : ""}
                >
                    Summary
                </Link>
                {user ? (
                    <>
                        <span style={{ color: "#E87E24", fontWeight: 600, fontSize: "0.85rem" }}>
                            {user}
                        </span>
                        <button onClick={handleLogout}>Logout</button>
                    </>
                ) : (
                    <Link
                        to="/login"
                        className={location.pathname === "/login" ? "active" : ""}
                    >
                        Login
                    </Link>
                )}
            </div>
        </nav>
    );
}
