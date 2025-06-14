import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { CustomerPayment } from "./customer/CustomerPayment";
import { CustomerTransaction } from "./customer/CustomerTransaction";
import { CustomerWallet } from "./customer/CustomerWallet";
import { Dashboard } from "./merchant/Dashboard";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/merchants/merchant-sidebar";

export function CustomerHome() {
    return (
        <SidebarProvider>
            <AppSidebar />
            <main
                style={{
                    width: "-webkit-fill-available",
                    height: "auto",
                }}
            >
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/customer/wallet" element={<CustomerWallet />} />
                    <Route path="/customer/transactions" element={<CustomerTransaction />} />
                    <Route path="/custormer/payments" element={<CustomerPayment />} />
                </Routes>
            </main>
        </SidebarProvider>
    );
}
