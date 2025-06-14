import { Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Dashboard } from "./merchant/Dashboard";
import { Wallets } from "./merchant/Wallets";
import { Payments } from "./merchant/Payments";
import { Reports } from "./merchant/Reports";
import { Transactions } from "./merchant/Transactions";
import { Settings } from "./merchant/Settings";
import { CreateWallet } from "./customer/CreateWallet";

export function MerchantHome() {
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
                    <Route path="/createwallet" element={<CreateWallet />} />
                    <Route path="/wallets" element={<Wallets />} />
                    <Route path="/payments" element={<Payments />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/transactions" element={<Transactions />} />
                    <Route path="/settings" element={<Settings />} />
                </Routes>
            </main>
        </SidebarProvider>
    );
}
