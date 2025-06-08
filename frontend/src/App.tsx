import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"

import { Login } from "./pages/Login"
import { AdminDashboard } from "./pages/admin/AdminDashboard"
import { Businesses } from "./pages/admin/Businesses"

import { Dashboard } from "./pages/merchant/Dashboard"
import { Wallets } from "./pages/merchant/Wallets"
import { WalletDetails } from "./pages/merchant/WalletDetails"
import { CreditWallet } from "./pages/merchant/CreditWallet"
import { DebitWallet } from "./pages/merchant/DebitWallet"
import { Transactions } from "./pages/merchant/Transactions"
import { Splash } from "./pages/Splash"

function App() {

    return (
        <Router>
            <Routes>
            <Route path="*" element={<Login />} />
                <Route path="/test-splash" element={<Splash />} />
                <Route path="/login" element={<Login />} />

                <Route path="/admin/dashboard" element={<AdminDashboard />} />
                <Route path="/admin/businesses" element={<Businesses />} />

                <Route path="/merchant/dashboard" element={<Dashboard />} />
                <Route path="/merchant/wallets" element={<Wallets />} />
                <Route path="/merchant/walletdetails" element={<WalletDetails />} />
                <Route path="/merchant/creditwallet" element={<CreditWallet />} />
                <Route path="/merchant/debitwallet" element={<DebitWallet />} />
                <Route path="/merchant/transactions" element={<Transactions />} />
            </Routes>
        </Router>
    )
}

export default App
