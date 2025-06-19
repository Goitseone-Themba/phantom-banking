export type UserRole = "admin" | "merchant" | "customer";

export interface AuthUser {
    id: string;
    username: string;
    role: UserRole;
}

export interface AuthTokens {
    access: string;
    refresh: string;
}
