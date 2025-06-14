import { TransactionsTable, transactionsTableFormat } from "@/components/transactions-table"



export function CustomerPayment() {

    const dummyTransactions: transactionsTableFormat[] = [
        {
            transactionId: "TXN001",
            date: "2025-06-13",
            amount: 150.75,
            walletId: "WAL123",
            type: "credit",
            status: "completed"
        },
        {
            transactionId: "TXN002",
            date: "2025-06-12",
            amount: 89.99,
            walletId: "WAL456",
            type: "debit",
            status: "pending"
        },
        {
            transactionId: "TXN003",
            date: "2025-06-11",
            amount: 250.00,
            walletId: "WAL123",
            type: "credit",
            status: "completed"
        },
        {
            transactionId: "TXN004",
            date: "2025-06-10",
            amount: 45.50,
            walletId: "WAL789",
            type: "debit",
            status: "completed"
        },
        {
            transactionId: "TXN005",
            date: "2025-06-09",
            amount: 300.25,
            walletId: "WAL456",
            type: "credit",
            status: "pending"
        }
    ];

    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
            <h1 className="roboto-heading text-6xl font-bold">Customer Payment</h1>
            <p className="roboto-text text-accent-foreground">Manage your payments and transactions</p>

            <TransactionsTable tabledata={dummyTransactions} />
        </div>
    )

}
