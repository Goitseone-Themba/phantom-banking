import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import AdminDashboard from "./admin/AdminDashboard";
import { AdminSidebar } from "@/components/admin/admin-sidebar";

export function AdminHome() {
    return (
        <SidebarProvider>
            <AdminSidebar/>
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
