import {
    Users,
    Wallet,
    Receipt,
    TrendingUp,
    AlertTriangle,
    Plus,
    Download,
    Settings,
    ChartBar,
} from "lucide-react";
import { StatsCard } from "./statistics-component";
import { Key, ReactElement, JSXElementConstructor, ReactNode, ReactPortal } from "react";

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

export interface RecentTransactionsStats {
    id: "string";
    user: string;
    amount: number;
    time: string;
    status: "completed" | "failed" | "pending";
}
// Dashboard Overview Component
export function DashboardOverview({
    stats,
    recentTransactions,
}: {
    stats: DashBoardStats;
    recentTransaction: RecentTransactionsStats[];
}) {
    return (
        <div className="p-6 ml-64">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatsCard
                    title="Total Users"
                    value={stats.totalUsers.toLocaleString()}
                    change={12.5}
                    icon={Users}
                    trend="up"
                />
                <StatsCard
                    title="Active Wallets"
                    value={stats.totalWallets.toLocaleString()}
                    change={8.2}
                    icon={Wallet}
                    trend="up"
                />
                <StatsCard
                    title="Total Transactions"
                    value={stats.totalTransactions.toLocaleString()}
                    change={-2.1}
                    icon={Receipt}
                    trend="down"
                />
                <StatsCard
                    title="Platform Balance"
                    value={`$${stats.totalBalance.toLocaleString()}`}
                    change={15.3}
                    icon={TrendingUp}
                    trend="up"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Recent Transactions */}
                <div className="bg-white rounded-lg shadow">
                    <div className="p-6 border-b">
                        <h3 className="text-lg font-semibold text-gray-800">Recent Transactions</h3>
                    </div>
                    <div className="p-6">
                        <div className="space-y-4">
                            {recentTransactions.map(
                                (transaction: {
                                    id: Key | null | undefined;
                                    user:
                                        | string
                                        | number
                                        | bigint
                                        | boolean
                                        | ReactElement<unknown, string | JSXElementConstructor<any>>
                                        | Iterable<ReactNode>
                                        | Promise<
                                              | string
                                              | number
                                              | bigint
                                              | boolean
                                              | ReactPortal
                                              | ReactElement<unknown, string | JSXElementConstructor<any>>
                                              | Iterable<ReactNode>
                                              | null
                                              | undefined
                                          >
                                        | null
                                        | undefined;
                                    time:
                                        | string
                                        | number
                                        | bigint
                                        | boolean
                                        | ReactElement<unknown, string | JSXElementConstructor<any>>
                                        | Iterable<ReactNode>
                                        | ReactPortal
                                        | Promise<
                                              | string
                                              | number
                                              | bigint
                                              | boolean
                                              | ReactPortal
                                              | ReactElement<unknown, string | JSXElementConstructor<any>>
                                              | Iterable<ReactNode>
                                              | null
                                              | undefined
                                          >
                                        | null
                                        | undefined;
                                    amount: number;
                                    status:
                                        | string
                                        | number
                                        | bigint
                                        | boolean
                                        | ReactElement<unknown, string | JSXElementConstructor<any>>
                                        | Iterable<ReactNode>
                                        | Promise<
                                              | string
                                              | number
                                              | bigint
                                              | boolean
                                              | ReactPortal
                                              | ReactElement<unknown, string | JSXElementConstructor<any>>
                                              | Iterable<ReactNode>
                                              | null
                                              | undefined
                                          >
                                        | null
                                        | undefined;
                                }) => (
                                    <div key={transaction.id} className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                                                <span className="text-xs font-medium">
                                                    {transaction.user[0]}
                                                </span>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">
                                                    {transaction.user}
                                                </p>
                                                <p className="text-xs text-gray-500">{transaction.time}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p
                                                className={`text-sm font-medium ${
                                                    transaction.amount > 0
                                                        ? "text-green-600"
                                                        : "text-red-600"
                                                }`}
                                            >
                                                ${Math.abs(transaction.amount).toLocaleString()}
                                            </p>
                                            <span
                                                className={`inline-block px-2 py-1 text-xs rounded-full ${
                                                    transaction.status === "completed"
                                                        ? "bg-green-100 text-green-800"
                                                        : transaction.status === "pending"
                                                        ? "bg-yellow-100 text-yellow-800"
                                                        : "bg-red-100 text-red-800"
                                                }`}
                                            >
                                                {transaction.status}
                                            </span>
                                        </div>
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                </div>

                {/* System Alerts */}
                <div className="bg-white rounded-lg shadow">
                    <div className="p-6 border-b">
                        <h3 className="text-lg font-semibold text-gray-800">System Alerts</h3>
                    </div>
                    <div className="p-6">
                        <div className="space-y-4">
                            {alertsData.map((alert) => (
                                <div key={alert.id} className="flex items-start space-x-3">
                                    <div
                                        className={`p-2 rounded-full ${
                                            alert.severity === "high"
                                                ? "bg-red-100"
                                                : alert.severity === "medium"
                                                ? "bg-yellow-100"
                                                : "bg-blue-100"
                                        }`}
                                    >
                                        <AlertTriangle
                                            className={`h-4 w-4 ${
                                                alert.severity === "high"
                                                    ? "text-red-600"
                                                    : alert.severity === "medium"
                                                    ? "text-yellow-600"
                                                    : "text-blue-600"
                                            }`}
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                                        <p className="text-xs text-gray-500">{alert.time}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
                        <Plus className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-600">Add User</span>
                    </button>
                    <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
                        <Download className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-600">Export Data</span>
                    </button>
                    <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
                        <Settings className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-600">System Config</span>
                    </button>
                    <button className="flex items-center justify-center space-x-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
                        <ChartBar className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-600">View Reports</span>
                    </button>
                </div>
            </div>
        </div>
    );
}
