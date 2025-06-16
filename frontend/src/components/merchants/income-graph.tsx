"use client";

import { TrendingUp, TrendingDown } from "lucide-react";
import { CartesianGrid, Line, LineChart, XAxis } from "recharts";

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

export const description = "Monthly spending and income analysis for your account.";

const chartData = [
    { month: "January", spending: 2845, income: 4200 },
    { month: "February", spending: 3120, income: 4200 },
    { month: "March", spending: 2680, income: 4350 },
    { month: "April", spending: 2450, income: 4200 },
    { month: "May", spending: 2890, income: 4200 },
    { month: "June", spending: 2755, income: 4400 },
];

const chartConfig = {
    spending: {
        label: "Spending",
        color: "red",
    },
    income: {
        label: "Income",
        color: "hsl(217, 91%, 75%)",
    },
} satisfies ChartConfig;

export function IncomeGraph() {
    const currentSpending = chartData[chartData.length - 1].spending;
    const previousSpending = chartData[chartData.length - 2].spending;
    const spendingChange = ((currentSpending - previousSpending) / previousSpending) * 100;
    const isSpendingDown = spendingChange < 0;

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Monthly Financial Overview</CardTitle>
                <CardDescription>January - June 2025</CardDescription>
            </CardHeader>
            <CardContent>
                <ChartContainer config={chartConfig}>
                    <LineChart
                        accessibilityLayer
                        data={chartData}
                        margin={{
                            left: 12,
                            right: 12,
                            top: 12,
                            bottom: 12,
                        }}
                    >
                        <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e0e7ff" />
                        <XAxis
                            dataKey="month"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                            tickFormatter={(value) => value.slice(0, 3)}
                            className="text-xs text-gray-500"
                        />
                        <ChartTooltip
                            cursor={false}
                            content={
                                <ChartTooltipContent
                                    hideLabel={false}
                                    formatter={(value, name) => [
                                        `$${value.toLocaleString()}`,
                                        chartConfig[name as keyof typeof chartConfig]?.label,
                                    ]}
                                />
                            }
                        />
                        <Line
                            dataKey="income"
                            type="natural"
                            stroke="var(--color-income)"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{
                                r: 4,
                                fill: "var(--color-income)",
                            }}
                        />
                        <Line
                            dataKey="spending"
                            type="natural"
                            stroke="var(--color-spending)"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{
                                r: 4,
                                fill: "var(--color-spending)",
                            }}
                        />
                    </LineChart>
                </ChartContainer>

                {/* Legend */}
                <div className="flex items-center justify-start gap-6 mt-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[hsl(217,91%,75%)]"></div>
                        <span className="text-gray-600">Income</span>
                        <span className="font-medium">${chartData[0].income.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-[hsl(217,91%,60%)]"></div>
                        <span className="text-gray-600">Spending</span>
                        <span className="font-medium">${chartData[0].spending.toLocaleString()}</span>
                    </div>
                </div>
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
                <div className="flex gap-2 leading-none font-medium">
                    {isSpendingDown ? (
                        <>
                            Spending decreased by {Math.abs(spendingChange).toFixed(1)}% this month
                            <TrendingDown className="h-4 w-4 text-green-600" />
                        </>
                    ) : (
                        <>
                            Spending increased by {spendingChange.toFixed(1)}% this month
                            <TrendingUp className="h-4 w-4 text-red-600" />
                        </>
                    )}
                </div>
                <div className="text-muted-foreground leading-none">
                    Current savings rate: $
                    {(
                        chartData[chartData.length - 1].income - chartData[chartData.length - 1].spending
                    ).toLocaleString()}{" "}
                    per month
                </div>
            </CardFooter>
        </Card>
    );
}
