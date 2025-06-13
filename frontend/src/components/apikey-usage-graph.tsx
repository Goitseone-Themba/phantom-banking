import { useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, TrendingUp, Clock } from "lucide-react";

const generateSampleData = () => {
    const data = [];
    const now = new Date();

    for (let i = 29; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);

        data.push({
            date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
            requests: Math.floor(Math.random() * 5000) + 1000,
            errors: Math.floor(Math.random() * 100) + 10,
            latency: Math.floor(Math.random() * 200) + 50,
        });
    }

    return data;
};

const apiKeys = [
    {
        id: "key-1",
        name: "Production API",
        usage: 89432,
        limit: 100000,
        status: "active",
    },
    {
        id: "key-2",
        name: "Development API",
        usage: 23456,
        limit: 50000,
        status: "active",
    },
    {
        id: "key-3",
        name: "Testing API",
        usage: 5678,
        limit: 25000,
        status: "active",
    },
    {
        id: "key-4",
        name: "Staging API",
        usage: 34567,
        limit: 40000,
        status: "warning",
    },
];

export default function APIUsageDashboard() {
    const [data] = useState(generateSampleData());
    const [selectedPeriod, setSelectedPeriod] = useState("30d");

    const totalRequests = data.reduce((sum, day) => sum + day.requests, 0);
    const avgLatency = Math.round(data.reduce((sum, day) => sum + day.latency, 0) / data.length);
    const errorRate = ((data.reduce((sum, day) => sum + day.errors, 0) / totalRequests) * 100).toFixed(2);

    const getUsageColor = (usage, limit) => {
        const percentage = (usage / limit) * 100;
        if (percentage >= 90) return "bg-red-500";
        if (percentage >= 70) return "bg-yellow-500";
        return "bg-green-500";
    };

    const getStatusBadge = (status) => {
        const variants = {
            active: "bg-green-100 text-green-800",
            warning: "bg-yellow-100 text-yellow-800",
            error: "bg-red-100 text-red-800",
        };
        return variants[status] || variants.active;
    };

    return (
        <div className="flex flex-nowrap flex-col gap-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">API Usage Dashboard</h1>
                    <p className="text-muted-foreground">
                        Monitor your API key usage and performance metrics
                    </p>
                </div>
                <Badge variant="outline" className="px-3 py-1">
                    Last updated: {new Date().toLocaleTimeString()}
                </Badge>
            </div>

            <div className="flex flex-nowrap flex-row justify-start gap-4">
                <Card className="flex-1">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalRequests.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">Last 30 days</p>
                    </CardContent>
                </Card>

                <Card className="flex-1">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
                        <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{avgLatency}ms</div>
                        <p className="text-xs text-muted-foreground">Response time</p>
                    </CardContent>
                </Card>

                <Card className="flex-1">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{errorRate}%</div>
                        <p className="text-xs text-muted-foreground">Error percentage</p>
                    </CardContent>
                </Card>
            </div>

            {/* Charts */}
            <Tabs defaultValue="requests" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="requests">Request Volume</TabsTrigger>
                    <TabsTrigger value="latency">Latency</TabsTrigger>
                    <TabsTrigger value="errors">Error Rate</TabsTrigger>
                </TabsList>

                <TabsContent value="requests">
                    <Card>
                        <CardHeader>
                            <CardTitle>API Requests Over Time</CardTitle>
                            <CardDescription>Daily request volume for the last 30 days</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip
                                        formatter={(value) => [value.toLocaleString(), "Requests"]}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="requests"
                                        stroke="#3b82f6"
                                        strokeWidth={2}
                                        dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="latency">
                    <Card>
                        <CardHeader>
                            <CardTitle>Response Latency</CardTitle>
                            <CardDescription>Average response time in milliseconds</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={400}>
                                <BarChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip
                                        formatter={(value) => [`${value}ms`, "Avg Latency"]}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Bar dataKey="latency" fill="#10b981" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="errors">
                    <Card>
                        <CardHeader>
                            <CardTitle>Error Count</CardTitle>
                            <CardDescription>Daily error occurrences</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={400}>
                                <LineChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip
                                        formatter={(value) => [value, "Errors"]}
                                        labelFormatter={(label) => `Date: ${label}`}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="errors"
                                        stroke="#ef4444"
                                        strokeWidth={2}
                                        dot={{ fill: "#ef4444", strokeWidth: 2, r: 4 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* API Keys List */}
            <Card>
                <CardHeader>
                    <CardTitle>API Key Usage</CardTitle>
                    <CardDescription>Current usage for each API key</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {apiKeys.map((key) => {
                            const usagePercentage = (key.usage / key.limit) * 100;
                            return (
                                <div
                                    key={key.id}
                                    className="flex items-center justify-between p-4 border rounded-lg"
                                >
                                    <div className="flex items-center space-x-4">
                                        <div>
                                            <h4 className="font-medium">{key.name}</h4>
                                            <p className="text-sm text-muted-foreground">
                                                {key.usage.toLocaleString()} / {key.limit.toLocaleString()}{" "}
                                                requests
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-4">
                                        <div className="w-32 bg-gray-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full ${getUsageColor(
                                                    key.usage,
                                                    key.limit
                                                )}`}
                                                style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                                            />
                                        </div>
                                        <span className="text-sm font-medium">
                                            {Math.round(usagePercentage)}%
                                        </span>
                                        <Badge className={getStatusBadge(key.status)}>{key.status}</Badge>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
