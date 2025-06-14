export type UserRole = "admin" | "merchant" | "customer";

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

