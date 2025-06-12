import { SearchBar } from "@/components/search-bar";

export function Transactions() {
    return (
        <div className="w-[inherit] h-auto flex flex-nowrap justify-start p-8 gap-6 flex-col ">
            <h1 className="roboto-heading text-6xl font-bold">Transactions</h1>
            <p className="roboto-text text-accent-foreground">
                Review and manage all transactions proccesed through your phantom banking platform.
            </p>
            <SearchBar placeholder="Search by transaction ID, wallet ID, amount or date."></SearchBar>
        </div>
    );
}
