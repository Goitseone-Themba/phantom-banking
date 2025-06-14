import { AuthTokens, AuthUser } from "@/types/auth";

export const saveAuth = (user: AuthUser, tokens: AuthTokens) => {
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("tokens", JSON.stringify(tokens));
};

export const clearAuth = () => {
  localStorage.removeItem("user");
  localStorage.removeItem("tokens");
};

export const getAuth = (): { user: AuthUser | null; tokens: AuthTokens | null } => {
  const user = localStorage.getItem("user");
  const tokens = localStorage.getItem("tokens");

  return {
    user: user ? JSON.parse(user) : null,
    tokens: tokens ? JSON.parse(tokens) : null,
  };
};

