import { SidebarProvider } from "@/components/ui/sidebar";
import AdminDashboard from "./admin/AdminDashboard";

export function AdminHome() {
    return (
        <SidebarProvider>
            <main
                style={{
                    width: "-webkit-fill-available",
                    height: "auto",
                }}
            >
                <AdminDashboard />
            </main>
        </SidebarProvider>
    );
}
