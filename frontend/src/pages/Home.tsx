import { Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Dashboard } from "./merchant/Dashboard";
import { Wallets } from "./merchant/Wallets";
import { Payments } from "./merchant/Payments";
import { Reports } from "./merchant/Reports";
import { Transactions } from "./merchant/Transactions";
import { Settings } from "./merchant/Settings";

export function Home() {
    return (
        <SidebarProvider>
            <AppSidebar />
            <main>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
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
