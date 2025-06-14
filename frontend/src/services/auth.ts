import { z } from "zod";
import { axiosInstance } from "./axios";

// Response schemas
const LoginResponseSchema = z.object({
    user_id: z.string().uuid(),
    message: z.string(),
});

const TokenResponseSchema = z.object({
    access: z.string(),
    refresh: z.string(),
});

const MerchantSignupResponseSchema = z.object({
    message: z.string(),
    user_id: z.string().uuid(),
    merchant_id: z.string().uuid(),
});

// Input types
export type LoginInput = {
    username_or_email: string;
    password: string;
};

export type Verify2FAInput = {
    user_id: string;
    otp: string;
};

export type MerchantSignupInput = {
    business_name: string;
    registration_number: string;
    contact_email: string;
    contact_phone: string;
    admin_name: string;
    admin_email: string;
    password: string;
    confirm_password: string;
};

// Auth service class for better encapsulation
class AuthService {
    private static instance: AuthService;
    private readonly TOKEN_KEY = "auth_tokens";
    private readonly USER_ID_KEY = "auth_user_id";

    private constructor() {}

    static getInstance(): AuthService {
        if (!AuthService.instance) {
            AuthService.instance = new AuthService();
        }
        return AuthService.instance;
    }

    // Login and get user_id for 2FA
    async login(input: LoginInput): Promise<{ user_id: string }> {
        try {
            const response = await axiosInstance.post("/auth/login/", input);
            const validatedData = LoginResponseSchema.parse(response.data);

            // Store user_id for 2FA
            localStorage.setItem(this.USER_ID_KEY, validatedData.user_id);

            return { user_id: validatedData.user_id };
        } catch (error) {
            if (error instanceof z.ZodError) {
                throw new Error("Invalid server response format");
            }
            throw error;
        }
    }

    // Verify 2FA and get tokens
    async verify2FA(input: Verify2FAInput): Promise<void> {
        try {
            const response = await axiosInstance.post("/auth/verify-2fa/", input);
            const validatedData = TokenResponseSchema.parse(response.data);

            // Store tokens
            localStorage.setItem(
                this.TOKEN_KEY,
                JSON.stringify({
                    access: validatedData.access,
                    refresh: validatedData.refresh,
                })
            );

            // Clear user_id after successful 2FA
            localStorage.removeItem(this.USER_ID_KEY);
        } catch (error) {
            if (error instanceof z.ZodError) {
                throw new Error("Invalid server response format");
            }
            throw error;
        }
    }

    // Register new merchant
    async registerMerchant(input: MerchantSignupInput): Promise<{ user_id: string; merchant_id: string }> {
        try {
            const response = await axiosInstance.post("/auth/merchant_signup/", input);
            const validatedData = MerchantSignupResponseSchema.parse(response.data);
            return {
                user_id: validatedData.user_id,
                merchant_id: validatedData.merchant_id,
            };
        } catch (error) {
            if (error instanceof z.ZodError) {
                throw new Error("Invalid server response format");
            }
            throw error;
        }
    }

    // Refresh access token
    async refreshToken(): Promise<void> {
        try {
            const tokens = this.getTokens();
            if (!tokens?.refresh) {
                throw new Error("No refresh token available");
            }

            const response = await axiosInstance.post("/auth/token/refresh/", {
                refresh: tokens.refresh,
            });

            const validatedData = TokenResponseSchema.parse(response.data);

            // Update tokens
            localStorage.setItem(
                this.TOKEN_KEY,
                JSON.stringify({
                    access: validatedData.access,
                    refresh: tokens.refresh, // Keep existing refresh token
                })
            );
        } catch (error) {
            if (error instanceof z.ZodError) {
                throw new Error("Invalid server response format");
            }
            throw error;
        }
    }

    // Logout and clear storage
    async logout(): Promise<void> {
        try {
            const tokens = this.getTokens();
            if (tokens?.refresh) {
                await axiosInstance.post("/auth/logout/", {
                    refresh_token: tokens.refresh,
                });
            }
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            // Always clear storage, even if logout request fails
            localStorage.removeItem(this.TOKEN_KEY);
            localStorage.removeItem(this.USER_ID_KEY);
        }
    }

    // Get stored tokens
    getTokens(): { access: string; refresh: string } | null {
        const tokensStr = localStorage.getItem(this.TOKEN_KEY);
        if (!tokensStr) return null;

        try {
            return JSON.parse(tokensStr);
        } catch {
            return null;
        }
    }

    // Get stored user_id
    getUserId(): string | null {
        return localStorage.getItem(this.USER_ID_KEY);
    }

    // Check if user is authenticated
    isAuthenticated(): boolean {
        return !!this.getTokens()?.access;
    }
}

// Export singleton instance
export const authService = AuthService.getInstance();
