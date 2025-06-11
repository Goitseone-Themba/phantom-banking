import { PayViaQrCode } from "@/components/qr-code-payment";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
export function Payments() {
    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
            <h1 className="roboto-heading text-6xl font-bold">Payments</h1>
            <p className="roboto-text text-accent-foreground">Manage and create payments for customers</p>

            <Tabs defaultValue="collect">
                <TabsList>
                    <TabsTrigger value="collect">Collect</TabsTrigger>
                    <TabsTrigger value="disburse">Disburse</TabsTrigger>
                </TabsList>
                <TabsContent value="collect">
                    <PayViaQrCode />
                </TabsContent>

                <TabsContent value="disburse">Somethind</TabsContent>
            </Tabs>
        </div>
    );
}
