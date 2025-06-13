import { Search } from "lucide-react";
import { InputHTMLAttributes } from "react";

type SearchBarProps = {
    placeholder: string;
} & InputHTMLAttributes<HTMLInputElement>;
export function SearchBar({ placeholder, ...props }: SearchBarProps) {
    return (
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
                type="text"
                className="roboto-text block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-100 focus:ring-1 focus:ring-grey-400 focus:border-grey-100"
                placeholder={placeholder}
                {...props}
            />
        </div>
    );
}
