import { Button } from "./ui/button";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { useEffect, useState, useRef } from "react";
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

export function EftPayment() {
    const [accountNumber, setAccountNumber] = useState("");
    const [bankName, setBankName] = useState("");
    const [amountDue, setAmountDue] = useState("");
    const [shouldErrorDialogOpen, setErrorDialogToOpen] = useState(false);
    const [eftError, setEFTError] = useState("");

    const [filteredBanks, setFilteredBanks] = useState([]);
    const [showDropdown, setShowDropdown] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const bankInputRef = useRef(null);
    const dropdownRef = useRef(null);

    const banks = [
        "Absa Bank",
        "FNB (First National Bank)",
        "BBS (Botswana Building Society)",
        "Standard Bank",
        "Nedbank",
        "Capitec Bank",
        "African Bank",
        "Discovery Bank",
        "TymeBank",
        "Bank Zero",
        "Investec",
        "Bidvest Bank",
    ];

    const startEFTTransaction = function (e: any) {
        e ? e.preventDefault() : null;
        if (accountNumber === "" || bankName === "" || amountDue === "") {
            return;
        }
        // Testing Backend Error
        setErrorDialogToOpen(true);
        setEFTError("invalid card number");
    };

    useEffect(() => {
        if (bankName.trim() === "") {
            setFilteredBanks([]);
            setShowDropdown(false);
            return;
        }

        const filtered = banks.filter((bank) => bank.toLowerCase().includes(bankName.toLowerCase()));

        setFilteredBanks(filtered);
        setShowDropdown(filtered.length > 0);
        setSelectedIndex(-1);
    }, [bankName]);

    const handleBankSelect = (bank: string) => {
        setBankName(bank);
        setShowDropdown(false);
        setSelectedIndex(-1);
        //@ts-ignore
        bankInputRef.current?.focus();
    };

    // Handle keyboard navigation
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (!showDropdown) return;

        switch (e.key) {
            case "ArrowDown":
                e.preventDefault();
                setSelectedIndex((prev) => (prev < filteredBanks.length - 1 ? prev + 1 : prev));
                break;
            case "ArrowUp":
                e.preventDefault();
                setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
                break;
            case "Enter":
                e.preventDefault();
                if (selectedIndex >= 0) {
                    handleBankSelect(filteredBanks[selectedIndex]);
                }
                break;
            case "Escape":
                setShowDropdown(false);
                setSelectedIndex(-1);
                break;
        }
    };

    // Handle clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            if (
                bankInputRef.current &&
                !bankInputRef.current.contains(target) &&
                dropdownRef.current &&
                !dropdownRef.current.contains(target)
            ) {
                setShowDropdown(false);
                setSelectedIndex(-1);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <form onSubmit={startEFTTransaction}>
            <div className="flex w-[inherit] flex-col gap-6">
                <Card className="w-2xl">
                    <CardHeader>
                        <span className="roboto-heading text-4xl font-bold">EFT Payment</span>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col w-auto h-auto gap-4">
                            <Label>Account number</Label>
                            <Input
                                value={accountNumber}
                                onChange={(e) => {
                                    setAccountNumber(e.target.value);
                                }}
                                required
                                type="number"
                                placeholder="Account number"
                            />

                            <Label>Bank Name</Label>
                            <div className="relative">
                                <Input
                                    ref={bankInputRef}
                                    value={bankName}
                                    onChange={(e) => {
                                        setBankName(e.target.value);
                                    }}
                                    onKeyDown={handleKeyDown}
                                    required
                                    type="text"
                                    placeholder="Bank Name"
                                    autoComplete="off"
                                />

                                {showDropdown && (
                                    <div
                                        ref={dropdownRef}
                                        className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
                                    >
                                        {filteredBanks.map((bank, index) => (
                                            <div
                                                key={bank}
                                                onClick={() => handleBankSelect(bank)}
                                                className={`px-4 py-2 cursor-pointer hover:bg-blue-50 ${
                                                    index === selectedIndex
                                                        ? "bg-blue-100 text-blue-900"
                                                        : "text-gray-900"
                                                }`}
                                            >
                                                {bank}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <Label>Amount to be paid</Label>
                            <Input
                                value={amountDue}
                                onChange={(e) => {
                                    setAmountDue(e.target.value);
                                }}
                                required
                                type="number"
                                placeholder="Enter amount to be paid"
                            />

                            <AlertDialog open={shouldErrorDialogOpen}>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>
                                            An error has occurred whilst trying to initiate the EFT Payment
                                        </AlertDialogTitle>
                                    </AlertDialogHeader>
                                    <AlertDialogDescription>
                                        The issue is: {eftError}
                                    </AlertDialogDescription>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel
                                            onClick={() => {
                                                setErrorDialogToOpen(false);
                                            }}
                                        >
                                            Cancel
                                        </AlertDialogCancel>
                                        <AlertDialogAction onClick={startEFTTransaction}>
                                            Try Again
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>

                            <Button
                                onClick={() => {
                                    setErrorDialogToOpen(false);
                                    startEFTTransaction(null);
                                }}
                                className="w-auto"
                            >
                                Initiate EFT Payment
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </form>
    );
}
