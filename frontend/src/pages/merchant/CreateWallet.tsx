import { CreateWalletForm } from "@/components/payments/create-wallet-form";

export function CreateWallet() {
    return (
        <div className="flex flex-nowrap flex-col gap-6 p-8">
            <CreateWalletForm></CreateWalletForm>
        </div>
    );
}
