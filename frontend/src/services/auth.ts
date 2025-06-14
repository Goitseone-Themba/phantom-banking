import axios from "axios"
import { setTokens, clearTokens, getRefreshToken } from "@/lib/tokenStorage"

interface LoginPayload {
    email: string
    password: string
}

interface OTPPayload {
    user_id: string
    otp: string
}

interface LoginResponse {
    user_id: string
    message: string
}

interface AuthTokens {
    access: string
    refresh: string
}

interface RegisterMerchantPayload {
    business_name: string
    registration_number: string
    contact_email: string
    contact_phone: string
    admin_name: string
    admin_email: string
    password: string
    confirm_password: string
}

async function login(payload: LoginPayload): Promise<LoginResponse> {
    const response = await axios.post("/auth/login/", payload)
    return response.data
}

export async function verify2FA(payload: OTPPayload): Promise<AuthTokens> {
    const response = await axios.post("/auth/verify-2fa/", payload)
    const { access, refresh } = response.data
    setTokens(access, refresh)
    return { access, refresh }
}

export async function logout(): Promise<void> {
    try {
        const refresh = getRefreshToken();
        if (!refresh) throw new Error("No refresh token found");
        await axios.post("/auth/logout/", { refresh_token: refresh });
    } catch (_) {
    } finally {
        clearTokens()
    }
}

export async function registerMerchant(payload: RegisterMerchantPayload) {
    const response = await axios.post("/auth/merchant_signup/", payload)
    return response.data
}

export async function verifyEmail(token: string) {
    const response = await axios.post("/auth/verify-email/", { token })
    return response.data
}

export async function requestPasswordReset(email: string) {
    const response = await axios.post("/auth/request_password_reset/", { email })
    return response.data
}

export async function resetPassword(
    token: string,
    new_password: string,
    confirm_password: string
) {
    const response = await axios.post("/auth/reset_password/", {
        token,
        new_password,
        confirm_password,
    })
    return response.data
}

export async function refreshToken(): Promise<string> {
    const refresh = getRefreshToken()
    if (!refresh) throw new Error("No refresh token available")
    const response = await axios.post("/auth/token/refresh/", { refresh })
    const access: string = response.data.access
    setTokens(access, refresh)
    return access
}

function setTokens(access: string, refresh: string) {
    localStorage.setItem("access_token", access)
    localStorage.setItem("refresh_token", refresh)
} 

function clearTokens() {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
} 

function getRefreshToken() {
    return localStorage.getItem("refresh_token")
}

export const auth = { login, verify2FA, logout, registerMerchant, verifyEmail, 
    requestPasswordReset, resetPassword }
