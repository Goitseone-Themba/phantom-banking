import { WalletTable } from "@/components/debit-wallets-table";
import { SearchBar } from "@/components/search-bar";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

import { useMemo, useState } from "react";
import { InfoCard } from "@/components/info-card";

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
    const [hasErrored, setToShowError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [isDialogOpen, setIsDialogOpen] = useState(false);

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

    const handleWalletCreation = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);

        fetch("/create-wallet", {
            method: "POST",
            body: formData,
        })
            .then(async (response) => {
                if (response.ok) {
                    console.log("Wallet created successfully");
                    setIsDialogOpen(false); // Close dialog on success
                    // You might want to refresh the wallet table here
                } else {
                    setIsDialogOpen(false);
                    console.log("Wallet creation failed");
                    // Handle error response
                    const errorText = await response.text();
                    setErrorMessage(`Failed to create wallet: ${errorText}`);
                    setToShowError(true);
                }
            })
            .catch((error) => {
                setToShowError(true);
                setErrorMessage(error.message || "An unexpected error occurred");
            });
    };

    return (
        <>
            <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
                <div className="flex flex-nowrap w-[-webkit-fill-available]">
                    <div className="flex-1">
                        <h1 className="roboto-heading text-6xl forced-color-adjust-auto">Wallets</h1>
                    </div>
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                            <Button className="bg-gray-200 text-gray-900" variant="secondary">
                                Create Wallet
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <form onSubmit={handleWalletCreation}>
                                <DialogHeader>
                                    <DialogTitle>Create a new Wallet.</DialogTitle>
                                    <DialogDescription>
                                        Enter all the relevant details to create a new wallet.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4">
                                    <div className="grid gap-3">
                                        <Label htmlFor="customername">Customer Name</Label>
                                        <Input id="customername" name="customername" required />
                                    </div>
                                    <div className="grid gap-3">
                                        <Label htmlFor="phonenumber">Phone number</Label>
                                        <Input id="phonenumber" name="phonenumber" required maxLength={8} />
                                    </div>
                                    <div className="grid gap-3">
                                        <Label htmlFor="initialbalance">Initial Balance (Optional)</Label>
                                        <Input
                                            id="initialbalance"
                                            name="initialbalance"
                                            type="number"
                                            maxLength={8}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <DialogClose asChild>
                                        <Button type="button" variant="outline">
                                            Cancel
                                        </Button>
                                    </DialogClose>
                                    <Button variant="default" type="submit">
                                        Create Wallet
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>
                <Tabs defaultValue="wallets" className="w-[-webkit-fill-available]">
                    <TabsList>
                        <TabsTrigger value="wallets">Wallets</TabsTrigger>
                        <TabsTrigger value="credit">Your Credit Wallet</TabsTrigger>
                        <TabsTrigger value="debit">Your Debit Wallet</TabsTrigger>
                    </TabsList>
                    <TabsContent value="wallets">
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
                    </TabsContent>
                    <TabsContent value="credit">
                        <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                            <h2 className="text-3xl roboto-text">Your Credit Wallet</h2>
                            <InfoCard title="Your Credit Balance" value="5400"></InfoCard>
                        </div>
                    </TabsContent>
                    <TabsContent value="debit">
                        <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                            TODO
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
            <AlertDialog open={hasErrored} onOpenChange={setToShowError}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>
                            An error has occurred while trying to create a new wallet.
                        </AlertDialogTitle>
                        <AlertDialogDescription>{errorMessage}</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Report This Issue</AlertDialogCancel>
                        <AlertDialogAction>Close & Try Again</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    );
}
