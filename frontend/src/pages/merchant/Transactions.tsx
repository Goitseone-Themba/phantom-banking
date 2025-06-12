import { SearchBar } from "@/components/search-bar";
import { TransactionsTable, type transactionsTableFormat } from "@/components/transactions-table";
import { useMemo, useState } from "react";
const transactions: transactionsTableFormat[] = [
    {
        transactionId: "TXN001",
        date: "June 12, 2025 10:30 AM",
        amount: 150.75,
        walletId: "W4A7B",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN002",
        date: "June 12, 2025 8:15 AM",
        amount: 89.99,
        walletId: "W2C9D",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN003",
        date: "June 11, 2025 4:45 PM",
        amount: 250.0,
        walletId: "W4A7B",
        type: "credit",
        status: "pending",
    },
    {
        transactionId: "TXN004",
        date: "June 11, 2025 2:20 PM",
        amount: 45.5,
        walletId: "W8E1F",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN005",
        date: "June 11, 2025 11:30 AM",
        amount: 500.0,
        walletId: "W5G3H",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN006",
        date: "June 10, 2025 7:45 PM",
        amount: 32.25,
        walletId: "W2C9D",
        type: "debit",
        status: "pending",
    },
    {
        transactionId: "TXN007",
        date: "June 10, 2025 1:15 PM",
        amount: 175.8,
        walletId: "W9J4K",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN008",
        date: "June 10, 2025 9:30 AM",
        amount: 67.4,
        walletId: "W8E1F",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN009",
        date: "June 9, 2025 5:20 PM",
        amount: 300.0,
        walletId: "W4A7B",
        type: "credit",
        status: "pending",
    },
    {
        transactionId: "TXN010",
        date: "June 9, 2025 12:45 PM",
        amount: 124.75,
        walletId: "W6L2M",
        type: "debit",
        status: "completed",
    },
    {
        transactionId: "TXN011",
        date: "June 8, 2025 8:10 PM",
        amount: 85.0,
        walletId: "W5G3H",
        type: "credit",
        status: "completed",
    },
    {
        transactionId: "TXN012",
        date: "June 8, 2025 3:35 PM",
        amount: 199.99,
        walletId: "W7N8P",
        type: "debit",
        status: "pending",
    },
];

export function Transactions() {
    const [searchTerm, setSearchTerm] = useState("");
    const filteredTransactions = useMemo(() => {
        if (searchTerm === "") {
            return transactions;
        }
        return transactions.filter((transaction) => {
            const searchValue = searchTerm.toLowerCase();
            return (
                transaction.transactionId.toLowerCase().includes(searchValue) ||
                transaction.walletId.toLowerCase().includes(searchValue)
            );
        });
    }, [searchTerm]);

    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col ">
            <h1 className="roboto-heading text-6xl font-bold">Transactions</h1>
            <p className="roboto-text text-accent-foreground">
                Review and manage all transactions proccesed through your phantom banking platform.
            </p>
            <SearchBar
                value={searchTerm}
                onChange={(e) => {
                    setSearchTerm(e.target.value);
                }}
                placeholder="Search by transaction ID, wallet ID, amount or date."
            ></SearchBar>
            <TransactionsTable tabledata={filteredTransactions}></TransactionsTable>
        </div>
    );
}
