import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Login } from "./pages/Login";
import { ForgotPassword } from "./pages/ForgotPassword";
import { SignUp } from "./pages/SignUp";
import { ProtectedRoute } from "./context/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { MerchantHome } from "./pages/MerchantHome";
import { CustomerHome } from "./pages/CustomerHome";
import { AdminHome } from "./pages/AdminHome";
function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* <Route path="*" element={<MerchantHome />} /> */}
                    <Route path="*" element={<Login />} />
                    <Route path="/signup" element={<SignUp />} />
                    <Route path="/forgotpassword" element={<ForgotPassword />} />

                    <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
                        <Route path="/admin" element={<AdminHome />} />
                    </Route>

                    <Route element={<ProtectedRoute allowedRoles={["merchant"]} />}>
                        <Route path="/merchant" element={<MerchantHome />} />
                    </Route>

                    <Route element={<ProtectedRoute allowedRoles={["customer"]} />}>
                        <Route path="/merchant" element={<CustomerHome />} />
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
