import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth, LoginPayload } from "@/services/auth";
import { sanitizeInput } from "@/lib/helpers";
import { saveAuth } from "@/lib/storage";
import { AuthTokens, AuthUser, UserRole } from "@/types/auth";

type LoginStage = "credentials" | "otp";

export function LoginForm() {
    const navigate = useNavigate();
    const [stage, setStage] = useState<LoginStage>("credentials");
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const handleUserLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        setError("");
        setIsLoading(true);

        try {
            const formData = new FormData(e.currentTarget);
            const username = sanitizeInput(formData.get("username") as string);
            const password = sanitizeInput(formData.get("password") as string);
            const loginInfo: LoginPayload = {
                username: username,
                password: password,
            };
            const requestLogin = auth.login(loginInfo);
            requestLogin
                .then((response) => {
                    if (!response.success) {
                        setError("Invalid Login Credentials; Password or Username Is Incorrect.");
                    }
                    const authenticatedUser: AuthUser = {
                        id: String(response.data.user.id),
                        username: response.data.user.username,
                        role: response.data.user.user_type as UserRole,
                    };
                    const authenticatedTokens: AuthTokens = {
                        access: response.data.access,
                        refresh: response.data.refresh,
                    };
                    saveAuth(authenticatedUser, authenticatedTokens);

                    if (response.data.user.is_mfa_verified) {
                        //@ts-ignore
                        if (response.data.user.user_type === "STAFF") {
                            navigate("/merchant");
                        } else if (response.data.user.user_type === "USER") {
                            navigate("/customer");
                        } else {
                            navigate("/admin");
                        }
                        return;
                    } else {
                        setStage("otp");
                    }
                })
                .catch((error) => {
                    setError(error);
                })
                .finally(() => {
                    setIsLoading(false);
                });
        } catch (error: any) {
            setError(error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleOTPSubmit = function () {};
    return (
        <div className="space-y-6">
            <div className="space-y-2 text-center">
                <h1 className="text-2xl font-bold">{stage === "credentials" ? "Login" : "Enter OTP"}</h1>
                <p className="text-muted-foreground">
                    {stage === "credentials"
                        ? "Enter your credentials to continue"
                        : "Enter the 6-digit code from your authenticator app"}
                </p>
            </div>

            {error && (
                <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">{error}</div>
            )}

            {stage === "credentials" ? (
                <form onSubmit={handleUserLogin} className="space-y-4" noValidate>
                    <div className="space-y-2">
                        <label
                            htmlFor="username"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Username *
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            required
                            minLength={3}
                            maxLength={50}
                            pattern="[a-zA-Z0-9._-]+"
                            autoComplete="username"
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
                            placeholder="Enter your username"
                            disabled={isLoading}
                        />
                    </div>

                    <div className="space-y-2">
                        <label
                            htmlFor="password"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Password *
                        </label>
                        <input
                            required
                            id="password"
                            name="password"
                            type="password"
                            minLength={8}
                            maxLength={128}
                            autoComplete="current-password"
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
                            placeholder="Enter your password"
                            disabled={isLoading}
                        />
                    </div>

                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                        disabled={isLoading}
                    >
                        {isLoading ? "Logging in..." : "Continue"}
                    </button>
                </form>
            ) : (
                <form onSubmit={handleOTPSubmit} className="space-y-4" noValidate>
                    <div className="space-y-2">
                        <label
                            htmlFor="otp"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            One-Time Password *
                        </label>
                        <input
                            id="otp"
                            name="otp"
                            type="text"
                            required
                            minLength={6}
                            maxLength={6}
                            pattern="[0-9]{6}"
                            inputMode="numeric"
                            autoComplete="one-time-code"
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50`}
                            placeholder="Enter 6-digit code"
                            disabled={isLoading}
                        />
                    </div>

                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                    >
                        {isLoading ? "Verifying..." : "Verify OTP"}
                    </button>
                </form>
            )}
        </div>
    );
}
