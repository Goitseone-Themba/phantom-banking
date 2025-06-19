import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "@/services/auth";


type LoginStage = "credentials" | "otp" | "complete"

export function LoginForm() {
    const navigate = useNavigate();
    const [stage, setStage] = useState<LoginStage>("credentials");
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    const handleCredentialsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        const formData = new FormData(e.currentTarget);
        const data = {
            username: formData.get("username") as string,
            password: formData.get("password") as string,
        };

        const loginInfo = login({
            username: data.username,
            password: data.password
        });
        loginInfo.then((response) => {
            setIsLoading(true)
            if (response.success === true){
                console.log("Login successful:", response);
                if (response.data.user.is_mfa_enabled){
                    setStage("complete")
                } else {
                    setStage("otp");
                }
            } else {
                setError("Invalid credentials. Please try again.");
            }
        }).catch((error) => {   
            console.error("Login error:", error);
            setError(`An error occurred: ${error.message || "Please try again."}`);
        }).finally(() => {
            setIsLoading(false);
        })
    };

    const handleOTPSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError("");
        setIsLoading(true);

        const formData = new FormData(e.currentTarget);
        const otpCode = formData.get("otp") as string;

        // Add your OTP verification logic here
        const baseUri = "http://127.0.0.1:8000/api/v1";

        try {
            const response = await fetch(`${baseUri}/auth/verify-otp/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ otp: otpCode }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log("OTP verification successful:", responseData);
                // Navigate to dashboard or home page
                navigate("/dashboard");
            } else {
                const errorResponse = await response.json();
                setError(errorResponse.detail || "Invalid OTP. Please try again.");
            }
        } catch (err) {
            console.error("Network error during OTP verification:", err);
            setError("Network error. Please check your connection and try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="space-y-2 text-center">
                <h1 className="text-2xl font-bold">{stage === "credentials" ? "Login" : "Enter OTP"}</h1>
                <p className="text-muted-foreground">
                    {stage === "credentials"
                        ? "Enter your credentials to continue"
                        : "Enter the 6-digit code sent to your username"}
                </p>
            </div>

            {error && (
                <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">{error}</div>
            )}

            {stage === "credentials" ? (
                <form onSubmit={handleCredentialsSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label
                            htmlFor="username"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Username
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            required
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            placeholder="Enter your username"
                            disabled={isLoading}
                        />
                    </div>
                    <div className="space-y-2">
                        <label
                            htmlFor="password"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            Password
                        </label>
                        <input
                            required
                            id="password"
                            name="password"
                            type="password" // Changed back to password type for security
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
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
                <form onSubmit={handleOTPSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label
                            htmlFor="otp"
                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                            One-Time Password
                        </label>
                        <input
                            id="otp"
                            name="otp"
                            type="text"
                            required
                            maxLength={6}
                            pattern="[0-9]*"
                            inputMode="numeric"
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            placeholder="Enter 6-digit code"
                            disabled={isLoading}
                        />
                    </div>
                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                        disabled={isLoading}
                    >
                        {isLoading ? "Verifying..." : "Verify OTP"}
                    </button>
                </form>
            )}
        </div>
    );
}
