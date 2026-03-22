import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DebatePage from "./pages/DebatePage";
import CategoriesPage from "./pages/CategoriesPage";
import OverallSummaryPage from "./pages/OverallSummaryPage";
import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/debate/:id" element={<DebatePage />} />
        <Route path="/categories" element={<CategoriesPage />} />
        <Route path="/overall-summary" element={<OverallSummaryPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
