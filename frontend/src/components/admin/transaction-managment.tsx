import { TransactionsTable, transactionsTableFormat } from "@/components/merchants/transactions-table";
import { SearchBar } from "@/components/search-bar";
import { Popover, PopoverTrigger, PopoverContent } from "@radix-ui/react-popover";
import { CalendarIcon, Calendar, CircleDollarSign } from "lucide-react";
import { useState, useMemo } from "react";
import { Button } from "react-day-picker";
import { Label } from "recharts";
import { Input } from "../ui/input";
export function TransactionManagement() {
    return (
        <div className="p-6 ml-64">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Transaction Management</h3>
                <p className="text-gray-600">Monitor and manage all platform transactions.</p>
            </div>

            {/* Placeholder for transaction management content */}
            <Transactions />
        </div>
    );
}

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

function Transactions() {
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
            <SearchBar
                value={searchTerm}
                onChange={(e) => {
                    setSearchTerm(e.target.value);
                }}
                placeholder="Search by transaction ID, wallet ID, or amount."
            />
            <div className="flex flex-row flex-nowrap gap-4 min-w-auto"></div>
            <TransactionsTable tabledata={filteredTransactions} />
        </div>
    );
}
