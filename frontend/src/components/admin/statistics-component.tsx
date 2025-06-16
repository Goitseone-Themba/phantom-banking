import { TrendingDown, TrendingUp } from "lucide-react";

interface StatisticsCard {
    title: string;
    value: string;
    change: number;
    icon: any;
    trend: "up" | "down";
    className?: "" | undefined;
}

// Icon type is a valid Lucid Icon Element

export function StatsCard({ title, value, change, icon: Icon, trend, className }: StatisticsCard) {
    const isPositive = trend === "up";

    return (
        <div className={`bg-white rounded-lg shadow p-6 ${className ? className : ""}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-600">{title}</p>
                    <p className="text-2xl font-semibold text-gray-900">{value}</p>
                    {change && (
                        <div
                            className={`flex items-center mt-2 ${
                                isPositive ? "text-green-600" : "text-red-600"
                            }`}
                        >
                            {isPositive ? (
                                <TrendingUp className="h-4 w-4 mr-1" />
                            ) : (
                                <TrendingDown className="h-4 w-4 mr-1" />
                            )}
                            <span className="text-sm font-medium">{change}%</span>
                        </div>
                    )}
                </div>
                <div className={`p-3 rounded-full ${isPositive ? "bg-green-100" : "bg-blue-100"}`}>
                    <Icon className={`h-6 w-6 ${isPositive ? "text-green-600" : "text-blue-600"}`} />
                </div>
            </div>
        </div>
    );
}
