import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Login } from "./pages/Login";
import AdminDashboard from "./pages/admin/AdminDashboard";
import { MerchantHome } from "./pages/MerchantHome";
import { ForgotPassword } from "./pages/ForgotPassword";
import { SignUp } from "./pages/SignUp";
import { ProtectedRoute } from "./context/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Login />} />
                    <Route path="/signup" element={<SignUp />} />
                    <Route path="/forgotpassword" element={<ForgotPassword />} />
                    <Route path="/admin/dashboard" element={<AdminDashboard />} />

                    <Route element={<ProtectedRoute allowedRoles={["merchant"]} />}>
                        <Route path="/merchant" element={<MerchantHome />} />
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
