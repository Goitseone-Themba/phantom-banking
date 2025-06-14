import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Login } from "./pages/Login";
import AdminDashboard from "./pages/admin/AdminDashboard";
import { Businesses } from "./pages/admin/Businesses";
import { MerchantHome } from "./pages/MerchantHome";

import { ForgotPassword } from "./pages/ForgotPassword";
import { SignUp } from "./pages/SignUp";
import { CustomerHome } from "./pages/CustomerHome";
function App() {
    return (
        <Router>
            <Routes>
                <Route path="*" element={<MerchantHome />} />
                <Route path="/login" element={<Login />} />

                <Route path="/signup" element={<SignUp />} />
                <Route path="/customer/home" element={<CustomerHome />} />
                <Route path="/customer/home/createwallet" element={<CustomerHome />} />
                <Route path="/customer/home/wallets" element={<CustomerHome />} />
                <Route path="/customer/home/payments" element={<CustomerHome />} />
                <Route path="/customer/home/reports" element={<CustomerHome />} />
                <Route path="/customer/home/transactions" element={<CustomerHome />} />
                <Route path="forgotpassword" element={<ForgotPassword />} />
                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/admin/businesses" element={<Businesses />} />
            </Routes>
        </Router>
    );
}

export default App;
