import { StatsCard } from "@/components/admin/statistics-component";
import { IncomeGraph } from "@/components/merchants/income-graph";

import { PersonStanding, Wallet } from "lucide-react";

export function Dashboard() {
    return (
        <>
            <div
                style={{
                    display: "flex",
                    flexWrap: "nowrap",
                    padding: "25px",
                    width: "-webkit-fill-available",
                    height: "auto",
                    flexDirection: "column",
                    gap: "35px",
                }}
            >
                <div>
                    <h1 className="roboto-heading text-6xl text-black">DashBoard</h1>
                    <p
                        style={{
                            marginTop: "25px",
                        }}
                        className="text-foreground roboto-text"
                    >
                        Overveiw of your Phantom Banking activity.
                    </p>
                </div>

                <div
                    style={{
                        width: "-webkit-fill-available",
                        height: "auto",
                        display: "flex",
                        justifyContent: "space-between",
                        gap: "20px",
                    }}
                >
                    <StatsCard
                        title="Total Balance"
                        value="$56789"
                        change={8.2}
                        icon={Wallet}
                        trend="up"
                        //@ts-ignore
                        className="flex-1"
                    ></StatsCard>

                    <StatsCard
                        title="Transactions Today"
                        value="256"
                        change={42}
                        icon={PersonStanding}
                        trend="down"
                        //@ts-ignore
                        className="flex-1"
                    ></StatsCard>
                </div>

                <div>
                    <h4 className="roboto-heading text-4xl text-black">Transactions Trends</h4>
                    <div style={{ marginTop: "20px" }}>
                        <IncomeGraph />
                    </div>
                </div>
            </div>
        </>
    );
}
