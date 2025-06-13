import { ChartBar, Receipt, Home, Hourglass, Settings, Wallet, ChevronUp, User2 } from "lucide-react";
import { PhantomBankingLogo } from "./ui/sidebar-label";
import { Link } from "react-router-dom";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarTrigger,
    useSidebar,
} from "@/components/ui/sidebar";

import React, { useState } from "react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "./ui/dropdown-menu";

const items = [
    {
        title: "DashBoard",
        url: "/",
        icon: Home,
    },
    {
        title: "Wallets",
        url: "/wallets",
        icon: Wallet,
    },
    {
        title: "Payments",
        url: "/payments",
        icon: Hourglass,
    },
    {
        title: "Transactions",
        url: "/transactions",
        icon: Receipt,
    },
    {
        title: "Reports",
        url: "/reports",
        icon: ChartBar,
    },
    {
        title: "Settings",
        url: "/settings",
        icon: Settings,
    },
];

export function AppSidebar() {
    const [activeUrl, setActiveUrl] = React.useState(window.location.hash);
    const { toggleSidebar } = useSidebar();
    const [userName, setUserName] = useState("OARABILE INC");
    //setUserName("Oarabile Koore");
    React.useEffect(() => {
        const handleHashChange = () => {
            setActiveUrl(window.location.hash);
        };

        window.addEventListener("hashchange", handleHashChange);

        return () => {
            window.removeEventListener("hashchange", handleHashChange);
        };
    }, []);

    return (
        <Sidebar collapsible="icon" variant="floating">
            <SidebarContent>
                <SidebarGroup>
                    <SidebarTrigger>
                        <button onClick={toggleSidebar}>Toggle Sidebar</button>
                    </SidebarTrigger>
                    <PhantomBankingLogo></PhantomBankingLogo>
                    <br></br>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {items.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton asChild>
                                        <Link
                                            style={{
                                                height: "3rem",
                                                backgroundColor:
                                                    activeUrl === item.url ? "#f0f0f0" : "transparent",
                                                color: activeUrl === item.url ? "black" : "inherit",
                                                borderRadius: "0.5rem",
                                                paddingLeft: "1rem",
                                                display: "flex",
                                                alignItems: "center",
                                                gap: "0.5rem",
                                                transition: "background-color 0.2s, color 0.2s",
                                            }}
                                            to={item.url}
                                            onClick={() => setActiveUrl(item.url)}
                                        >
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </Link>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <SidebarMenuButton>
                                    <User2 /> {userName}
                                    <ChevronUp className="ml-auto" />
                                </SidebarMenuButton>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent side="top" className="w-[--radix-popper-anchor-width]">
                                <DropdownMenuItem>
                                    <span>Billing</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                    <span>Sign out</span>
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    );
}
