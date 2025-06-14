export function AdminHeader({ activeSection }) {
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
                    <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-700">Admin User</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
