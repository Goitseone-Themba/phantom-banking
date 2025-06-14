import * as React from "react";
import Link from "next/link";
import { CircleCheckIcon, CircleHelpIcon, CircleIcon } from "lucide-react";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

export function About() {
    return (
        <>
            <div>
                <NavigationMenu>
                    <NavigationMenuList>
                        <NavigationMenuTrigger asChild></NavigationMenuTrigger>
                    </NavigationMenuList>
                </NavigationMenu>
            </div>
        </>
    );
}
