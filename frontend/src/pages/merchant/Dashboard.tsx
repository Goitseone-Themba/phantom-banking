import { BankingSpendingChart } from "@/components/chart-line";
import { InfoCard } from "@/components/info-card";

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
                    gap: "35px", // Consistent spacing between all children
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
                    <InfoCard title="Active Wallets" value="1000"></InfoCard>
                    <InfoCard title="Total Balance" value="$56789"></InfoCard>
                    <InfoCard title="Transactions Today" value="256"></InfoCard>
                </div>

                <div>
                    <h4 className="roboto-heading text-4xl text-black">Transactions Trends</h4>
                    <div style={{ marginTop: "20px" }}>
                        <BankingSpendingChart />
                    </div>
                </div>
            </div>
        </>
    );
}
