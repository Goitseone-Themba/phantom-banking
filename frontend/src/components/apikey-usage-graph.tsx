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

interface APIKEYFormat {
    id: string;
    name: string;
    usage: number;
    limit: number;
    status: "warning" | "active";
}

interface HEALTHDATAFormat {
    errors: number;
    date: Date;
    latency: number;
    erros: number;
}

export default function APIUsageDashboard({
    apiData,
    heatlhData,
}: {
    apiData: APIKEYFormat[];
    heatlhData: HEALTHDATAFormat[];
}) {
    const totalRequests =   
    const getUsageColor = (usage: number, limit: number) => {
        const percentage = (usage / limit) * 100;
        if (percentage >= 90) return "bg-red-500";
        if (percentage >= 70) return "bg-yellow-500";
        return "bg-green-500";
    };

    const getStatusBadge = (status: "warning" | "active") => {
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
