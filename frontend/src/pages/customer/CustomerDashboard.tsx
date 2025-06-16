import { StatsCard } from "@/components/admin/statistics-component";
import { Wallet } from "lucide-react";

export function CustomerDashboard() {
    const userName = "Oarabile";
    return (
        <div className="flex flex-nowrap gap-8 p-6 flex-col">
            <h1 className="roboto-heading text-2xl">Hello {userName} Welcome To Your Phantom Wallet.</h1>

            <div className="flex flex-wrap gap-4 justify-between w-full">
                <StatsCard
                    title="Your Balance"
                    value="P1238"
                    icon={Wallet}
                    trend="down"
                    change={23}
                ></StatsCard>
            </div>
        </div>
    );
}
