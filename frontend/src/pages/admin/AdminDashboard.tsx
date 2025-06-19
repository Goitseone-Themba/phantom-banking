import { DashboardOverview } from "@/components/admin/dashboard-overview";
import { UserManagement, UserStats } from "@/components/admin/user-managemnet";
import { useState } from "react";
import { AdminHeader } from "@/components/admin/admin-header";
import { AdminSidebar } from "@/components/admin/admin-sidebar";
import { APIUsageAnalytics } from "@/components/admin/api-usage-analytics";
import { TransactionManagement } from "@/components/admin/transaction-managment";

// Mock data for dashboard
const dashboardStats: DashBoardStats = {
    totalUsers: 12847,
    totalWallets: 9834,
    totalTransactions: 45621,
    totalBalance: 2847293.56,
    monthlyGrowth: 12.5,
    pendingTransactions: 23,
    activeUsers: 8934,
    revenueThisMonth: 45892.34,
};

const recentTransactions = [
    { id: "T12345", user: "Sophia Clark", amount: -1234.56, status: "completed", time: "2 min ago" },
    { id: "T12346", user: "Ethan Miller", amount: 789.01, status: "pending", time: "5 min ago" },
    { id: "T12347", user: "Olivia Davis", amount: -2456.78, status: "completed", time: "12 min ago" },
    { id: "T12348", user: "Liam Wilson", amount: 3012.34, status: "failed", time: "18 min ago" },
    { id: "T12349", user: "Ava Martinez", amount: -567.89, status: "completed", time: "25 min ago" },
];

const users: UserStats[] = [
    {
        id: 1,
        name: "Sophia Clark",
        email: "sophia@example.com",
        status: "active",
        wallets: 2,
        lastLogin: "2 hours ago",
    },
    {
        id: 2,
        name: "Ethan Miller",
        email: "ethan@example.com",
        status: "inactive",
        wallets: 1,
        lastLogin: "2 days ago",
    },
    {
        id: 3,
        name: "Olivia Davis",
        email: "olivia@example.com",
        status: "active",
        wallets: 3,
        lastLogin: "1 hour ago",
    },
    {
        id: 4,
        name: "Liam Wilson",
        email: "liam@example.com",
        status: "suspended",
        wallets: 1,
        lastLogin: "1 week ago",
    },
];

export interface DashBoardStats {
    totalUsers: number;
    totalWallets: number;
    totalTransactions: 45621;
    totalBalance: number;
    monthlyGrowth: number;
    pendingTransactions: number;
    activeUsers: number;
    revenueThisMonth: number;
}

// Main Admin Dashboard Component
export default function AdminDashboard() {
    const [activeSection, setActiveSection] = useState<string>("dashboard");
    const renderContent = () => {
        console.log("I was re-rendered proof: ");
        switch (activeSection) {
            case "users":
                return <UserManagement users={users} />;
            case "transactions":
                return <TransactionManagement />;
            case "apiusage":
                return <APIUsageAnalytics />;

            default:
                return <DashboardOverview stats={dashboardStats} recentTransactions={recentTransactions} />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <AdminSidebar activeSection={activeSection} setActiveSection={setActiveSection} />
            <AdminHeader activeSection={activeSection} />
            {renderContent()}
        </div>
    );
}
