import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/merchants/merchant-sidebar";
import AdminDashboard from "./admin/AdminDashboard";

export function AdminHome() {
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
                    <Route path="/dashboard" element={<AdminDashboard />} />
                </Routes>
            </main>
        </SidebarProvider>
    );
}
