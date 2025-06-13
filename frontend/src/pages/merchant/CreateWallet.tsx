import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useRef } from "react";

export function CreateWallet() {
    return (
        <div className="flex flex-nowrap flex-col gap-6 p-8">
            <h1 className="roboto-heading text-2xl font-bold">Create a New Wallet</h1>
            <p className="roboto-text text-accent-foreground font-light">
                Enter the user's details in here:
            </p>
            <Label>Users Name</Label>
            <Input></Input>
        </div>
    );
}
