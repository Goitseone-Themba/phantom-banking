import React, { useState } from "react";
import {
    ChartBar,
    Receipt,
    BadgeHelp,
    Home,
    Hourglass,
    Settings,
    Wallet,
    Users,
    AlertTriangle,
    TrendingUp,
    TrendingDown,
    Search,
    Filter,
    Plus,
    Eye,
    Edit,
    Trash2,
    Download,
    Bell,
} from "lucide-react";

import { StatsCard } from "@/components/statistics-component";

const recentTransactions = [
    { id: "T12345", user: "Sophia Clark", amount: -1234.56, status: "completed", time: "2 min ago" },
    { id: "T12346", user: "Ethan Miller", amount: 789.01, status: "pending", time: "5 min ago" },
    { id: "T12347", user: "Olivia Davis", amount: -2456.78, status: "completed", time: "12 min ago" },
    { id: "T12348", user: "Liam Wilson", amount: 3012.34, status: "failed", time: "18 min ago" },
    { id: "T12349", user: "Ava Martinez", amount: -567.89, status: "completed", time: "25 min ago" },
];

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

// Sidebar Component
function AdminSidebar({ activeSection, setActiveSection }) {
    const menuItems = [
        { id: "dashboard", title: "Dashboard", icon: Home },
        { id: "users", title: "User Management", icon: Users },
        { id: "wallets", title: "Wallet Management", icon: Wallet },
        { id: "transactions", title: "Transactions", icon: Receipt },
        { id: "payments", title: "Payment Systems", icon: Hourglass },
        { id: "reports", title: "Reports & Analytics", icon: ChartBar },
        { id: "settings", title: "System Settings", icon: Settings },
        { id: "support", title: "Help & Support", icon: BadgeHelp },
    ];

    return (
        <div className="w-64 bg-white shadow-lg h-screen fixed left-0 top-0 z-50">
            <div className="p-6 border-b">
                <h1 className="text-xl font-bold text-gray-800">Phantom Banking</h1>
                <p className="text-sm text-gray-500">Admin Dashboard</p>
            </div>

            <nav className="mt-6">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => setActiveSection(item.id)}
                        className={`w-full flex items-center px-6 py-3 text-left hover:bg-blue-50 transition-colors ${
                            activeSection === item.id
                                ? "bg-blue-100 border-r-2 border-blue-500 text-blue-700"
                                : "text-gray-700"
                        }`}
                    >
                        <item.icon className="h-5 w-5 mr-3" />
                        {item.title}
                    </button>
                ))}
            </nav>
        </div>
    );
}

// Header Component
function AdminHeader({ activeSection }) {
    return (
        <div className="bg-white shadow-sm border-b px-6 py-4 ml-64">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-semibold text-gray-800 capitalize">
                        {activeSection.replace("-", " ")}
                    </h2>
                    <p className="text-gray-500">Manage your banking platform</p>
                </div>

                <div className="flex items-center space-x-4">
                    <div className="relative">
                        <Bell className="h-6 w-6 text-gray-400 cursor-pointer hover:text-gray-600" />
                        <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
                    </div>

                    <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-sm font-medium">A</span>
                        </div>
                        <span className="text-sm font-medium text-gray-700">Admin User</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

// User Management Component
function UserManagement() {
    const [searchTerm, setSearchTerm] = useState("");
    const [filterStatus, setFilterStatus] = useState("all");

    const users = [
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

    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-800">User Management</h3>
                        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add User</span>
                        </button>
                    </div>

                    <div className="flex items-center space-x-4 mt-4">
                        <div className="relative flex-1 max-w-md">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search users..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="all">All Status</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                            <option value="suspended">Suspended</option>
                        </select>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    User
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Wallets
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Last Login
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {users.map((user) => (
                                <tr key={user.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                                                <span className="text-white text-sm font-medium">
                                                    {user.name[0]}
                                                </span>
                                            </div>
                                            <div className="ml-3">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {user.name}
                                                </div>
                                                <div className="text-sm text-gray-500">{user.email}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                                user.status === "active"
                                                    ? "bg-green-100 text-green-800"
                                                    : user.status === "inactive"
                                                    ? "bg-gray-100 text-gray-800"
                                                    : "bg-red-100 text-red-800"
                                            }`}
                                        >
                                            {user.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {user.wallets}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {user.lastLogin}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <div className="flex items-center space-x-2">
                                            <button className="text-blue-600 hover:text-blue-900">
                                                <Eye className="h-4 w-4" />
                                            </button>
                                            <button className="text-gray-600 hover:text-gray-900">
                                                <Edit className="h-4 w-4" />
                                            </button>
                                            <button className="text-red-600 hover:text-red-900">
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

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

function PaymentSystems() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Payment Systems</h3>
                <p className="text-gray-600">Configure and manage payment methods and integrations.</p>
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

function HelpSupport() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Help & Support</h3>
                <p className="text-gray-600">Manage customer support tickets and help resources.</p>
            </div>
        </div>
    );
}

// Main Admin Dashboard Component
export default function AdminDashboard() {
    const [activeSection, setActiveSection] = useState("users");

    const renderContent = () => {
        switch (activeSection) {
            case "dashboard":
                return <DashboardOverview />;
            case "users":
                return <UserManagement />;
            case "wallets":
                return <WalletManagement />;
            case "transactions":
                return <TransactionManagement />;
            case "payments":
                return <PaymentSystems />;
            case "reports":
                return <ReportsAnalytics />;
            case "settings":
                return <SystemSettings />;
            case "support":
                return <HelpSupport />;
            default:
                return <DashboardOverview />;
        }
    };

    return <div className="min-h-screen bg-gray-50">{renderContent()}</div>;
}
