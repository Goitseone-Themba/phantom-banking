import { WalletTable } from "@/components/debit-wallets-table";
import { SearchBar } from "@/components/search-bar";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function Wallets() {
    return (
        <>
            <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
                <div className=" flex flex-nowrap w-[-webkit-fill-available]">
                    <div className="flex-1">
                        <h1 className="roboto-heading text-6xl forced-color-adjust-auto">Wallets</h1>
                    </div>
                    <Button
                        className="bg-gray-200 text-gray-900"
                        variant="secondary"
                        onClick={createWallet}
                    >
                        Create Wallet
                    </Button>
                </div>
                <Tabs defaultValue="wallets" className="w-[-webkit-fill-available]">
                    <TabsList>
                        <TabsTrigger value="wallets">Wallets</TabsTrigger>
                        <TabsTrigger value="credit">Your Credit Wallet</TabsTrigger>
                        <TabsTrigger value="debit">Your Debit Wallet</TabsTrigger>
                    </TabsList>
                    <TabsContent value="wallets">
                        <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                            <SearchBar placeholder="Search by name, phone and wallet ID" />
                            <WalletTable />
                        </div>
                    </TabsContent>
                    <TabsContent value="credit">
                        <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                            TODO
                        </div>
                    </TabsContent>
                    <TabsContent value="debit">
                        <div className="width-[-webkit-fill-available] flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                            TODO
                        </div>
                    </TabsContent>
                </Tabs>
            </div>
        </>
    );
}

function createWallet() {}
