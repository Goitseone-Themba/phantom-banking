import type { JSX, ReactNode } from "react";

export function SideBarMainLayout(...children: ReactNode[]): JSX.Element {
    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col">
            {children}
        </div>
    );
}
