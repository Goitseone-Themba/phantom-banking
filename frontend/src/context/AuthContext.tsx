import { createContext, useContext, useEffect, useState } from "react";
import { AuthUser, AuthTokens, UserRole } from "@/types/auth";
import { getAuth, saveAuth, clearAuth } from "@/lib/storage";
import { login, verify2FA, logout as backendLogout } from "@/services/auth";

interface AuthContextType {
  user: AuthUser | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  userRole: UserRole | null;
  loginUser: (email: string, password: string) => Promise<string>; // returns user_id
  verifyOtp: (userId: string, otp: string) => Promise<void>;
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

  const loginUser = async (email: string, password: string): Promise<string> => {
    const res = await login(email, password); // expects { user_id }
    return res.user_id;
  };

  const verifyOtp = async (userId: string, otp: string) => {
    const res = await verify2FA(userId, otp); // expects { access, refresh, user }
    saveAuth(res.user, { access: res.access, refresh: res.refresh });
    setUser(res.user);
    setTokens({ access: res.access, refresh: res.refresh });
  };

  const logout = async () => {
    if (tokens?.refresh) {
      await backendLogout(tokens.refresh);
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
        verifyOtp,
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

