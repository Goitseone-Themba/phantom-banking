import APIUsageDashboard from "@/components/apikey-usage-graph";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TabsContent } from "@radix-ui/react-tabs";
import { useRef } from "react";
import { toast } from "sonner";

export function Settings() {
    const businessName = useRef("OARABILE INC");
    const businessPhoneNumber = useRef("71763170");
    const businessEmail = useRef("oarabilekoore@protonmail.com");
    const businessLocation = useRef("Botswana, Mogoditshane, Ledumadumane");

    const businessAPIKEY = useRef(15616848484156);

    const doesUserHavePermissionsToEditSettings = useRef<boolean | undefined>(false);

    const copyAPIKEY = () => {
        navigator.clipboard.writeText(String(businessAPIKEY.current));
    };

    const generateNewApiKey = function () {
        toast("New API KEY Generated", {
            description: "You are advised not to share it, and update all code reliant on it.",
            action: {
                label: "Copy",
                onclick: copyAPIKEY(),
            },
        });
    };
    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col ">
            <h1 className="roboto-heading text-6xl font-bold">Business Settings</h1>
            <p className="roboto-text text-accent-foreground">
                Manage your business account and information
            </p>

            <Tabs defaultValue="contactinfo" className="w-4xl">
                <TabsList>
                    <TabsTrigger value="contactinfo">Contact Information</TabsTrigger>
                    <TabsTrigger value="apikeys">API Keys & Usage</TabsTrigger>
                    <TabsTrigger value="permissions">Manage User Permissions</TabsTrigger>
                </TabsList>

                <TabsContent value="contactinfo">
                    <div className="width-auto flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                        <h2 className="roboto-heading text-3xl">Contact Information</h2>

                        <Label>Business Name</Label>
                        <Input
                            value={businessName.current}
                            disabled={doesUserHavePermissionsToEditSettings}
                            onChange={(e) => {}}
                        ></Input>

                        <Label>Contact Email</Label>
                        <Input
                            value={businessEmail.current}
                            disabled={doesUserHavePermissionsToEditSettings}
                            onChange={(e) => {}}
                        ></Input>

                        <Label>Phone Number</Label>
                        <Input
                            value={businessPhoneNumber.current}
                            disabled={doesUserHavePermissionsToEditSettings}
                            onChange={(e) => {}}
                        ></Input>

                        <Label>Business Location</Label>
                        <Input
                            value={businessLocation.current}
                            disabled={doesUserHavePermissionsToEditSettings}
                            onChange={(e) => {}}
                        ></Input>

                        <Button>Update Contact Information</Button>
                    </div>
                </TabsContent>

                <TabsContent value="apikeys">
                    <div className="width-auto flex flex-nowrap justify-start pt-4 gap-6 flex-col">
                        <APIUsageDashboard></APIUsageDashboard>
                        <Label>Api Key</Label>
                        <Input
                            disabled={doesUserHavePermissionsToEditSettings}
                            value={businessAPIKEY.current}
                        ></Input>
                        <Button onClick={generateNewApiKey}>Generate new API KEY</Button>
                    </div>
                </TabsContent>

                <TabsContent value="permissions"></TabsContent>
            </Tabs>
        </div>
    );
}
