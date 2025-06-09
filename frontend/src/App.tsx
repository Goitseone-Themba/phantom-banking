import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Login } from "./pages/Login";
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { Businesses } from "./pages/admin/Businesses";
import { Home } from "./pages/Home";
import { About } from "./pages/About";
function App() {
    return (
        <Router>
            <Routes>
                <Route path="*" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/about" element={<About />} />
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/admin/businesses" element={<Businesses />} />
            </Routes>
        </Router>
    );
}

export default App;
