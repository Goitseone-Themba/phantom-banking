import { WalletTable } from "@/components/payments/debit-wallets-table";
import { SearchBar } from "@/components/search-bar";
import { Button } from "@/components/ui/button";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

const customerWallets = [
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

export function Wallets() {
    const [searchTerm, setSearchTerm] = useState("");
    const filteredWallets = useMemo(() => {
        if (!searchTerm) {
            return customerWallets;
        }

        return customerWallets.filter((wallet) => {
            const searchCase = searchTerm.toLowerCase();
            return (
                wallet.balance.toLocaleLowerCase().includes(searchCase) ||
                wallet.customerName.toLocaleLowerCase().includes(searchCase) ||
                wallet.phoneNumber.toLocaleLowerCase().includes(searchCase) ||
                wallet.walletId.toLocaleLowerCase().includes(searchCase)
            );
        });
    }, [searchTerm]);

    return (
        <>
            <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
                <div className="flex flex-nowrap w-[-webkit-fill-available]">
                    <div className="flex-1">
                        <h1 className="roboto-heading text-6xl forced-color-adjust-auto">Wallets</h1>
                    </div>

                    <Button variant="default" type="submit">
                        <Link to="/createwallet"> Create Wallet</Link>
                    </Button>
                </div>

                <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                    <SearchBar
                        value={searchTerm}
                        onChange={(event) => {
                            setSearchTerm(event.target.value);
                        }}
                        placeholder="Search by name, phone and wallet ID"
                    />
                    <WalletTable wallets={filteredWallets} />
                </div>
            </div>
        </>
    );
}
