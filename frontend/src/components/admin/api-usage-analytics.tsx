import APIUsageDashboard from "./apikey-usage-graph";
import { type APIKEYFormat } from "./apikey-usage-graph";

// Random data for API keys
const apiKeys: APIKEYFormat[] = [
    {
        id: "key1",
        name: "Frontend Service",
        usage: 8500,
        limit: 10000,
        status: "active",
        date: "2024-06-05",
        latency: 230,
        errors: 5,
    },
    {
        id: "key2",
        name: "Backend Worker",
        usage: 9500,
        limit: 10000,
        status: "warning",
        date: "2024-06-05",
        latency: 230,
        errors: 5,
    },
    {
        id: "key3",
        name: "Mobile App",
        usage: 4200,
        limit: 10000,
        status: "active",
        date: "2024-06-02",
        latency: 190,
        errors: 2,
    },
    {
        id: "key4",
        name: "Partner Integration",
        usage: 7200,
        limit: 10000,
        status: "active",
        date: "2024-06-01",
        latency: 210,
        errors: 3,
    },
];

// Random data for charts (last 7 days as example)
const data = [
    { date: "2024-06-01", latency: 210, errors: 3 },
    { date: "2024-06-02", latency: 190, errors: 2 },
    { date: "2024-06-03", latency: 220, errors: 4 },
    { date: "2024-06-04", latency: 200, errors: 1 },
    { date: "2024-06-05", latency: 230, errors: 5 },
    { date: "2024-06-06", latency: 215, errors: 2 },
    { date: "2024-06-07", latency: 205, errors: 3 },
];

export function APIUsageAnalytics() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <APIUsageDashboard heatlhData={data} apiData={apiKeys}></APIUsageDashboard>
            </div>
        </div>
    );
}
