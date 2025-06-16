import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
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
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

export function EftPayment() {
    const [accountNumber, setAccountNumber] = useState("");
    const [bankName, setBankName] = useState("");
    const [amountDue, setAmountDue] = useState("");
    const [shouldErrorDialogOpen, setErrorDialogToOpen] = useState(false);
    const [eftError, setEFTError] = useState("");

    const startEFTTransaction = function (e: any) {
        e ? e.preventDefault() : null;
        if (accountNumber === "" || bankName === "" || amountDue === "") {
            return;
        }
        // Testing Backend Error
        setErrorDialogToOpen(true);
        setEFTError("invalid card number");
    };

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

                            <Select
                                defaultValue="First National Bank (FNB)"
                                onValueChange={(value) => {
                                    setBankName(value);
                                }}
                            >
                                <SelectTrigger className="w-auto">
                                    <SelectValue placeholder="Select a Bank" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectGroup>
                                        <SelectLabel>Select a Bank</SelectLabel>
                                        <SelectItem value="First National Bank (FNB)">
                                            First National Bank (FNB)
                                        </SelectItem>
                                        <SelectItem value="ABSA Bank">ABSA Bank</SelectItem>
                                        <SelectItem value="Standard Bank">Standard Bank</SelectItem>
                                        <SelectItem value="NedBank">NedBank</SelectItem>
                                        <SelectItem value="Capitec Bank">Capitec Bank</SelectItem>
                                    </SelectGroup>
                                </SelectContent>
                            </Select>

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

export function PayBackViaEft() {
    const [accountNumber, setAccountNumber] = useState("");
    const [bankName, setBankName] = useState("");
    const [amountDue, setAmountDue] = useState("");
    const [shouldErrorDialogOpen, setErrorDialogToOpen] = useState(false);
    const [eftError, setEFTError] = useState("");

    const startEFTTransaction = function (e: any) {
        e ? e.preventDefault() : null;

        alert("EFT Payment Done");
        // Testing Backend Error
        // setErrorDialogToOpen(true);
        // setEFTError("invalid card number");
    };

    return (
        <form onSubmit={startEFTTransaction}>
            <div className="flex w-[inherit] flex-col gap-6">
                <Card className="w-2xl">
                    <CardHeader>
                        <span className="roboto-heading text-4xl font-bold">Disburse/Payback Via EFT</span>
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

                            <Select
                                defaultValue="First National Bank (FNB)"
                                onValueChange={(value) => {
                                    setBankName(value);
                                }}
                            >
                                <SelectTrigger className="w-auto">
                                    <SelectValue placeholder="Select a Bank" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectGroup>
                                        <SelectLabel>Select a Bank</SelectLabel>
                                        <SelectItem value="First National Bank (FNB)">
                                            First National Bank (FNB)
                                        </SelectItem>
                                        <SelectItem value="ABSA Bank">ABSA Bank</SelectItem>
                                        <SelectItem value="Standard Bank">Standard Bank</SelectItem>
                                        <SelectItem value="NedBank">NedBank</SelectItem>
                                        <SelectItem value="Capitec Bank">Capitec Bank</SelectItem>
                                    </SelectGroup>
                                </SelectContent>
                            </Select>

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
