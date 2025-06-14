interface walletsFormat {
    walletId: string;
    customerName: string;
    phoneNumber: string;
    balance: string;
}
export function WalletTable({ wallets }: { wallets: walletsFormat[] }) {
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
                            <td className="p-4 align-middle [&:has([role=checkbox])]:pr-0" colSpan={3}>
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
