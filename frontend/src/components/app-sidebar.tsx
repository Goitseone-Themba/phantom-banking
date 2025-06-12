import { ChartBar, Receipt, BadgeHelp, Home, Hourglass, Settings, Wallet } from "lucide-react";
import { PhantomBankingLogo } from "./ui/sidebar-label";
import { Link } from "react-router-dom";
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarProvider,
} from "@/components/ui/sidebar";

import React from "react";

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
        <Sidebar>
            <SidebarContent>
                <SidebarGroup>
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
            <div>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton asChild>
                            <a
                                href=""
                                style={{
                                    height: "3rem",
                                    backgroundColor: activeUrl === "" ? "#f0f0f0" : "transparent",
                                    color: activeUrl === "" ? "black" : "inherit",
                                    borderRadius: "0.5rem",
                                    paddingLeft: "1rem",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "0.5rem",
                                    transition: "background-color 0.2s, color 0.2s",
                                }}
                                onClick={() => setActiveUrl("")}
                            >
                                <BadgeHelp />
                                <span>Help & Support</span>
                            </a>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </div>
        </Sidebar>
    );
}
