import axios from "axios";

export interface LoginPayload {
    username: string;
    password: string;
}

export interface LoginResponse {
    success: boolean;
    message: string;
    data: {
        refresh: string;
        access: string;
        user: {
            id: number;
            username: string;
            email: string;
            first_name: string;
            last_name: string;
            user_type: "customer" | "merchant" | "admin";
            is_active: boolean;
            is_email_verified: string | boolean;
            is_mfa_enabled: boolean;
            is_mfa_verified: boolean;
            requires_mfa_setup: boolean;
            created_at: Date;
            updated_at: Date;
            last_login: null;
        };
    };
}

export interface AuthTokens {
    access: string;
    refresh: string;
}

export interface RegisterMerchantPayload {
    business_name: string;
    registration_number: string;
    contact_email: string;
    contact_phone: string;
    admin_name: string;
    admin_email: string;
    password: string;
    confirm_password: string;
}

const baseUri = "http://127.0.0.1:8000/api";

async function login(payload: LoginPayload): Promise<LoginResponse> {
    const response = await axios.post(baseUri + "/auth/login/", payload, {
        headers: { "Content-Type": "application/json" },
    });
    return response.data as Promise<LoginResponse>;
}

async function logout(): Promise<void> {
    try {
        const refresh = getRefreshToken();
        if (!refresh) throw new Error("No refresh token found");
        await axios.post("/auth/logout/", { refresh_token: refresh });
    } catch (_) {
    } finally {
        clearTokens();
    }
}

async function registerMerchant(payload: RegisterMerchantPayload) {
    const response = await axios.post("/auth/merchant_signup/", payload);
    return response.data;
}

async function verifyEmail(token: string) {
    const response = await axios.post("/auth/verify-email/", { token });
    return response.data;
}

async function requestPasswordReset(email: string) {
    const response = await axios.post("/auth/request_password_reset/", { email });
    return response.data;
}

async function resetPassword(token: string, new_password: string, confirm_password: string) {
    const response = await axios.post("/auth/reset_password/", {
        token,
        new_password,
        confirm_password,
    });
    return response.data;
}

async function refreshToken(): Promise<string> {
    const refresh = getRefreshToken();
    if (!refresh) throw new Error("No refresh token available");
    const response = await axios.post("/auth/token/refresh/", { refresh });
    const access: string = response.data.access;
    setTokens(access, refresh);
    return access;
}

function setTokens(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

export const auth = {
    login,
    logout,
    registerMerchant,
    verifyEmail,
    requestPasswordReset,
    resetPassword,
    refreshToken,
};
