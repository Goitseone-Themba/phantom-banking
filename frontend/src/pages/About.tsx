import APIUsageDashboard from "@/components/apikey-usage-graph";

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

export function About() {
    return <APIUsageDashboard apiData={apiKeys}></APIUsageDashboard>;
}
