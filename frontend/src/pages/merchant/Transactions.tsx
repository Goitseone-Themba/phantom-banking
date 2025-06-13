import { SearchBar } from "@/components/search-bar";
import { TransactionsTable, type transactionsTableFormat } from "@/components/transactions-table";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent } from "@/components/ui/popover";
import { PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, CircleDollarSign } from "lucide-react";
import { useMemo, useState } from "react";

const transactions: transactionsTableFormat[] = [
    {
        transactionId: "TXN001",
        date: "2025-06-12",
        amount: 150.75,
        walletId: "W4A7B",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN002",
        date: "2025-06-12",
        amount: 89.99,
        walletId: "W2C9D",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN003",
        date: "2025-06-11",
        amount: 250.0,
        walletId: "W4A7B",
        type: "credit",
        status: "pending",
    },
    {
        transactionId: "TXN004",
        date: "2025-06-11",
        amount: 45.5,
        walletId: "W8E1F",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN005",
        date: "2025-06-11",
        amount: 500.0,
        walletId: "W5G3H",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN006",
        date: "2025-06-10",
        amount: 32.25,
        walletId: "W2C9D",
        type: "debit",
        status: "pending",
    },
    {
        transactionId: "TXN007",
        date: "2025-06-10",
        amount: 175.8,
        walletId: "W9J4K",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN008",
        date: "2025-06-10",
        amount: 67.4,
        walletId: "W8E1F",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN009",
        date: "2025-06-09",
        amount: 300.0,
        walletId: "W4A7B",
        type: "credit",
        status: "pending",
    },
    {
        transactionId: "TXN010",
        date: "2025-06-09",
        amount: 124.75,
        walletId: "W6L2M",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN011",
        date: "2025-06-08",
        amount: 85.0,
        walletId: "W5G3H",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN012",
        date: "2025-06-08",
        amount: 199.99,
        walletId: "W7N8P",
        type: "debit",
        status: "pending",
    },
];

export function Transactions() {
    const [searchTerm, setSearchTerm] = useState("");
    const [searchDate, setSearchDate] = useState<Date | undefined>(undefined);
    const [open, setOpen] = useState(false);
    const [searchAmountMinimum, setSearchAmountMinimum] = useState<number | undefined>(undefined);
    const [searchAmountMaximum, setSearchAmountMaximum] = useState<number | undefined>(undefined);
    const [shouldAmountFilterOpen, setAmountFilterToOpen] = useState(false);
    const filteredTransactions = useMemo(() => {
        let filtered = transactions;

        if (searchTerm !== "") {
            const searchValue = searchTerm.toLowerCase();
            filtered = filtered.filter(
                (transaction) =>
                    transaction.transactionId.toLowerCase().includes(searchValue) ||
                    transaction.walletId.toLowerCase().includes(searchValue) ||
                    transaction.amount.toString().includes(searchValue)
            );
        }

        if (searchDate) {
            const selectedDateStr = searchDate.toISOString().split("T")[0];
            filtered = filtered.filter((transaction) => transaction.date === selectedDateStr);
        }

        if (searchAmountMinimum !== undefined || searchAmountMaximum !== undefined) {
            // If both values are zero, don't apply any amount filtering (show whole table)
            if (!(searchAmountMinimum === 0 && searchAmountMaximum === 0)) {
                filtered = filtered.filter((transaction) => {
                    const amount = transaction.amount;
                    const min = searchAmountMinimum ?? 0;
                    const max = searchAmountMaximum ?? Infinity;
                    return amount >= min && amount <= max;
                });
            }
        }
        return filtered;
    }, [searchTerm, searchDate, searchAmountMaximum, searchAmountMinimum]);

    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col ">
            <h1 className="roboto-heading text-6xl font-bold">Transactions</h1>
            <p className="roboto-text text-accent-foreground">
                Review and manage all transactions processed through your phantom banking platform.
            </p>
            <SearchBar
                value={searchTerm}
                onChange={(e) => {
                    setSearchTerm(e.target.value);
                }}
                placeholder="Search by transaction ID, wallet ID, or amount."
            />
            <div className="flex flex-row flex-nowrap gap-4 min-w-auto">
                <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                        <Button
                            variant="outline"
                            data-empty={!searchDate}
                            className="data-[empty=true]:text-muted-foreground w-min justify-start text-left font-normal"
                        >
                            <CalendarIcon />
                            {searchDate ? searchDate.toLocaleDateString() : "Filter transaction by Date"}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                        <Calendar
                            mode="single"
                            selected={searchDate}
                            defaultMonth={searchDate}
                            onSelect={(date) => {
                                setSearchDate(date);
                                setOpen(false);
                            }}
                            className="rounded-lg border shadow-sm"
                        />
                    </PopoverContent>
                </Popover>

                <Popover open={shouldAmountFilterOpen} onOpenChange={setAmountFilterToOpen}>
                    <PopoverTrigger asChild>
                        <Button variant="outline">
                            {" "}
                            <CircleDollarSign />
                            Filter by Amount
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80">
                        <div className="grid gap-4">
                            <div className="space-y-2">
                                <h4 className="leading-none font-medium">Amount Filter</h4>
                                <p className="text-muted-foreground text-sm">
                                    Filter transactions by a range.
                                </p>
                            </div>
                            <div className="grid gap-2">
                                <div className="grid grid-cols-3 items-center gap-4">
                                    <Label htmlFor="minimum">Minimum</Label>
                                    <Input
                                        onKeyUp={(ev) => {
                                            if (ev.code === "Enter") {
                                                setAmountFilterToOpen(false);
                                            }
                                        }}
                                        onChange={(e) => {
                                            setSearchAmountMinimum(Number(e.target.value));
                                        }}
                                        value={searchAmountMinimum || 1}
                                        id="minimum"
                                        className="col-span-2 h-8"
                                    />
                                </div>
                                <div className="grid grid-cols-3 items-center gap-4">
                                    <Label htmlFor="maximum">Maximum</Label>
                                    <Input
                                        onKeyUp={(ev) => {
                                            if (ev.code === "Enter") {
                                                setAmountFilterToOpen(false);
                                            }
                                        }}
                                        onChange={(e) => {
                                            setSearchAmountMaximum(Number(e.target.value));
                                        }}
                                        id="maximum"
                                        value={searchAmountMaximum || Infinity}
                                        className="col-span-2 h-8"
                                    />
                                </div>
                            </div>
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
            <TransactionsTable tabledata={filteredTransactions} />
        </div>
    );
}
