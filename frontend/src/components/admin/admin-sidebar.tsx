import { ChartBar, Receipt, BadgeHelp, Home, Hourglass, Settings, Wallet, Users } from "lucide-react";

export function AdminSidebar({ activeSection, setActiveSection }) {
    const menuItems = [
        { id: "dashboard", title: "Dashboard", icon: Home },
        { id: "users", title: "User Management", icon: Users },
        { id: "wallets", title: "Wallet Management", icon: Wallet },
        { id: "transactions", title: "Transactions", icon: Receipt },

        { id: "reports", title: "Reports & Analytics", icon: ChartBar },
        { id: "settings", title: "System Settings", icon: Settings },
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
