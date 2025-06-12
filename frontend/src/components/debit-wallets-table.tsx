const wallets = [
    {
        walletId: "W12345",
        customerName: "Sophia Clark",
        phoneNumber: "+1-555-123-4567",
        balance: "$1,234.56",
    },
    {
        walletId: "W67890",
        customerName: "Ethan Miller",
        phoneNumber: "+1-555-987-6543",
        balance: "$789.01",
    },
    {
        walletId: "W24680",
        customerName: "Olivia Davis",
        phoneNumber: "+1-555-246-8013",
        balance: "$3,456.78",
    },
    {
        walletId: "W13579",
        customerName: "Liam Wilson",
        phoneNumber: "+1-555-135-7924",
        balance: "$9,012.34",
    },
    {
        walletId: "W97531",
        customerName: "Ava Martinez",
        phoneNumber: "+1-555-975-3186",
        balance: "$567.89",
    },
    {
        walletId: "W86420",
        customerName: "Noah Anderson",
        phoneNumber: "+1-555-864-2097",
        balance: "$2,345.67",
    },
    {
        walletId: "W36925",
        customerName: "Isabella Thomas",
        phoneNumber: "+1-555-369-2518",
        balance: "$8,901.23",
    },
    {
        walletId: "W74185",
        customerName: "Jackson Jackson",
        phoneNumber: "+1-555-741-8529",
        balance: "$4,567.89",
    },
    {
        walletId: "W52963",
        customerName: "Mia White",
        phoneNumber: "+1-555-529-6340",
        balance: "$1,012.34",
    },
    {
        walletId: "W15935",
        customerName: "Aiden Harris",
        phoneNumber: "+1-555-159-3561",
        balance: "$6,789.01",
    },
];

export function WalletTable() {
    const totalBalance = wallets.reduce((sum, wallet) => {
        const amount = parseFloat(wallet.balance.replace(/[$,]/g, ""));
        return sum + amount;
    }, 0);

    return (
        <div className="w-full">
            <div className="rounded-md border">
                <table className="w-full caption-bottom text-sm">
                    <thead className="[&_tr]:border-b">
                        <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0">
                                Wallet ID
                            </th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0">
                                Customer Name
                            </th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0">
                                Phone Number
                            </th>
                            <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0">
                                Balance
                            </th>
                        </tr>
                    </thead>
                    <tbody className="[&_tr:last-child]:border-0">
                        {wallets.map((wallet) => (
                            <tr
                                key={wallet.walletId}
                                className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                            >
                                <td className="p-4 align-middle [&:has([role=checkbox])]:pr-0">
                                    <div className="font-medium text-green-600">{wallet.walletId}</div>
                                </td>
                                <td className="p-4 align-middle [&:has([role=checkbox])]:pr-0">
                                    {wallet.customerName}
                                </td>
                                <td className="p-4 align-middle [&:has([role=checkbox])]:pr-0">
                                    <div className="text-green-600">{wallet.phoneNumber}</div>
                                </td>
                                <td className="p-4 text-right align-middle [&:has([role=checkbox])]:pr-0">
                                    <div className="text-green-600">{wallet.balance}</div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot>
                        <tr className="border-b font-medium [&>td]:last:border-b-0">
                            <td className="p-4 align-middle [&:has([role=checkbox])]:pr-0" colSpan="3">
                                Total
                            </td>
                            <td className="p-4 text-right align-middle [&:has([role=checkbox])]:pr-0">
                                $
                                {totalBalance.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                })}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    );
}
