import { useState } from "react";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { ChevronDownIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

export function CreateWalletForm() {
    const [phoneNumber, setPhoneNumber] = useState<number | undefined>(undefined);
    const [email, setEmail] = useState<string | undefined>(undefined);
    const [id, setId] = useState<number | undefined>(undefined);
    const [name, setName] = useState<string | undefined>(undefined);
    const [open, setOpen] = useState(false);
    const [date, setDate] = useState<Date | undefined>(undefined);

    const createWallet = () => {};
    return (
        <form
            onSubmit={(event) => {
                event.preventDefault();
                createWallet();
            }}
        >
            <div className="flex flex-nowrap p-8 gap-6 flex-col w-2xl">
                <h1 className="roboto-heading text-6xl">Create a new Wallet.</h1>
                <Label>Customer's Name</Label>
                <Input
                    required
                    onChange={(e) => {
                        setName(e.target.value);
                    }}
                    value={name}
                    placeholder="Add the customers name here"
                ></Input>

                <Label>Customer's Email</Label>

                <Input
                    required
                    type="email"
                    value={email}
                    onChange={(e) => {
                        setEmail(e.target.value);
                    }}
                    placeholder="Add the customers email here"
                ></Input>

                <Label>Customer's Identification Number</Label>

                <Input
                    required
                    type="number"
                    value={id}
                    onChange={(e) => {
                        setId(Number(e.target.value));
                    }}
                    placeholder="Add the customers id number here"
                ></Input>

                <Label>Customer's Phone Number</Label>

                <Input
                    required
                    type="number"
                    value={phoneNumber}
                    onChange={(e) => {
                        setPhoneNumber(Number(e.target.value));
                    }}
                    placeholder="Add the customers phone number here"
                ></Input>

                <Label>Customer's Birthdate Here</Label>
                <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                        <Button variant="outline">
                            <ChevronDownIcon /> Add BirthDate
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto overflow-hidden p-0" align="start">
                        <Calendar
                            mode="single"
                            selected={date}
                            captionLayout="dropdown"
                            onSelect={(date) => {
                                setOpen(false);
                                setDate(date);
                            }}
                        ></Calendar>
                    </PopoverContent>
                </Popover>

                <Button
                    variant="default"
                    onClick={() => {
                        createWallet();
                    }}
                >
                    Create Wallet
                </Button>
            </div>
        </form>
    );
}
