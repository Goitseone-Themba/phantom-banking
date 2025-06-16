import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

export interface transactionsTableFormat {
    transactionId: string;
    date: string;
    amount: number;
    walletId: string;
    type: "credit" | "debit";
    status: "completed" | "pending";
}

export function TransactionsTable({ tabledata }: { tabledata: transactionsTableFormat[] }) {
    return (
        <Table>
            <TableCaption>
                A table of recent transactions using that have gone through your merchant account.
            </TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Wallet ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {tabledata.map((transaction) => (
                    <TableRow key={transaction.transactionId}>
                        <TableCell className="font-medium">{transaction.transactionId}</TableCell>
                        <TableCell>{transaction.date}</TableCell>
                        <TableCell>{transaction.amount}</TableCell>
                        <TableCell>{transaction.walletId}</TableCell>
                        <TableCell>{transaction.type}</TableCell>
                        <TableCell>{transaction.status}</TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}
