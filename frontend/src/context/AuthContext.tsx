import { createContext, useContext, useEffect, useState } from "react";
import { AuthUser, AuthTokens, UserRole } from "@/types/auth";
import { getAuth, saveAuth, clearAuth } from "@/lib/storage";
import { auth } from "@/services/auth";

interface AuthContextType {
    user: AuthUser | null;
    tokens: AuthTokens | null;
    isAuthenticated: boolean;
    userRole: UserRole | null;
    loginUser: (username: string, password: string) => Promise<string>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [tokens, setTokens] = useState<AuthTokens | null>(null);

    useEffect(() => {
        const { user, tokens } = getAuth();
        if (user && tokens) {
            setUser(user);
            setTokens(tokens);
        }
    }, []);

    const loginUser = async (username: string, password: string): Promise<string> => {
        const res = await auth.login({
            username,
            password,
        });
        return String(res.data.user.id);
    };

    const logout = async () => {
        if (tokens?.refresh) {
            await auth.logout();
        }
        clearAuth();
        setUser(null);
        setTokens(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                tokens,
                isAuthenticated: !!user,
                userRole: user?.role ?? null,
                loginUser,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
    return ctx;
};
