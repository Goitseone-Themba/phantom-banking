import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { CustomerPayment } from "./customer/CustomerPayment";
import { CustomerTransaction } from "./customer/CustomerTransaction";
import { CustomerWallet } from "./customer/CustomerWallet";
import { CustomerDashboard } from "./customer/CustomerDashboard";

export function CustomerHome() {
    return (
        <main
            style={{
                width: "-webkit-fill-available",
                height: "auto",
            }}
        >
            <Routes>
                <Route path="/" element={<CustomerDashboard />} />
                <Route path="/customer/wallet" element={<CustomerWallet />} />
                <Route path="/customer/transactions" element={<CustomerTransaction />} />
                <Route path="/custormer/payments" element={<CustomerPayment />} />
            </Routes>
        </main>
    );
}
