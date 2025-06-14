import { DashboardOverview } from "@/components/admin/dashboard-overview";
import { UserManagement, UserStats } from "@/components/admin/user-managemnet";
import { useState } from "react";
import { AdminHeader } from "@/components/admin/admin-header";
import { AdminSidebar } from "@/components/admin/admin-sidebar";
// Sidebar Component

// Header Component

// Placeholder components for other sections
function WalletManagement() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Wallet Management</h3>
                <p className="text-gray-600">
                    Manage user wallets, view balances, and handle wallet operations.
                </p>
            </div>
        </div>
    );
}

function TransactionManagement() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Transaction Management</h3>
                <p className="text-gray-600">Monitor and manage all platform transactions.</p>
            </div>
        </div>
    );
}

function ReportsAnalytics() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Reports & Analytics</h3>
                <p className="text-gray-600">Generate reports and view platform analytics.</p>
            </div>
        </div>
    );
}

function SystemSettings() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">System Settings</h3>
                <p className="text-gray-600">Configure system-wide settings and preferences.</p>
            </div>
        </div>
    );
}

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

const alertsData = [
    {
        id: 1,
        type: "security",
        message: "Suspicious login attempt detected",
        severity: "high",
        time: "5 min ago",
    },
    { id: 2, type: "system", message: "Database backup completed", severity: "low", time: "1 hour ago" },
    {
        id: 3,
        type: "transaction",
        message: "Large transaction flagged for review",
        severity: "medium",
        time: "2 hours ago",
    },
];

// Main Admin Dashboard Component
export default function AdminDashboard() {
    const [activeSection] = useState(""); // Default active section
    const renderContent = () => {
        switch (activeSection) {
            case "users":
                return <UserManagement users={users} />;
            case "wallets":
                return <WalletManagement />;
            case "transactions":
                return <TransactionManagement />;
            case "reports":
                return <ReportsAnalytics />;
            case "settings":
                return <SystemSettings />;
            default:
                return <DashboardOverview stats={dashboardStats} recentTransactions={recentTransactions} />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <AdminSidebar activeSection={activeSection} setActiveSection={() => {}} />
            <AdminHeader activeSection={activeSection} />
            {renderContent()}
        </div>
    );
}
