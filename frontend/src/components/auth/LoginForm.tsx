import { useState, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "@/services/auth";
import DOMPurify from 'dompurify';

type LoginStage = "credentials" | "otp" | "complete";

const SecurityUtils = {
    // Input sanitization
    sanitizeInput: (input: string): string => {
        if (typeof input !== 'string') return '';
        
        // Remove null bytes, control characters, and normalize
        return input
            .replace(/\0/g, '') 
            .replace(/[\x00-\x1F\x7F]/g, '') 
            .trim()
            .substring(0, 255); 
    },

    // HTML escape for display (though React handles this automatically)
    escapeHtml: (unsafe: string): string => {
        return DOMPurify.sanitize(unsafe, { ALLOWED_TAGS: [] });
    },
    
    validateUsername: (username: string): { valid: boolean; error?: string } => {
        if (!username || username.length === 0) {
            return { valid: false, error: "Username is required" };
        }
        
        if (username.length < 3) {
            return { valid: false, error: "Username must be at least 3 characters" };
        }
        
        if (username.length > 50) {
            return { valid: false, error: "Username must be less than 50 characters" };
        }
        
        // Allow alphanumeric, underscore, hyphen, dot
        const usernamePattern = /^[a-zA-Z0-9._-]+$/;
        if (!usernamePattern.test(username)) {
            return { valid: false, error: "Username can only contain letters, numbers, dots, hyphens, and underscores" };
        }
        
        // Check for SQL injection patterns
        const sqlPatterns = [
            /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)/i,
            /(--|\*|\||;|'|"|<|>)/,
            /(\bOR\b|\bAND\b).*[=<>]/i
        ];
        
        for (const pattern of sqlPatterns) {
            if (pattern.test(username)) {
                return { valid: false, error: "Invalid characters detected in username" };
            }
        }
        
        return { valid: true };
    },

    // Password validation
    validatePassword: (password: string): { valid: boolean; error?: string } => {
        if (!password || password.length === 0) {
            return { valid: false, error: "Password is required" };
        }
        
        if (password.length < 8) {
            return { valid: false, error: "Password must be at least 8 characters" };
        }
        
        if (password.length > 128) {
            return { valid: false, error: "Password must be less than 128 characters" };
        }
        
        return { valid: true };
    },

    // OTP validation
    validateOTP: (otp: string): { valid: boolean; error?: string } => {
        if (!otp || otp.length === 0) {
            return { valid: false, error: "OTP is required" };
        }
        
        // Must be exactly 6 digits
        const otpPattern = /^[0-9]{6}$/;
        if (!otpPattern.test(otp)) {
            return { valid: false, error: "OTP must be exactly 6 digits" };
        }
        
        return { valid: true };
    },

    // Rate limiting
    checkRateLimit: (lastAttempt: number, minInterval: number = 2000): boolean => {
        const now = Date.now();
        return (now - lastAttempt) >= minInterval;
    }
};

export function LoginForm() {
    const navigate = useNavigate();
    const [stage, setStage] = useState<LoginStage>("credentials");
    const [error, setError] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);
    const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
    
    // Rate limiting
    const lastAttemptRef = useRef<number>(0);
    const attemptCountRef = useRef<number>(0);
    const maxAttemptsRef = useRef<number>(5);

    // Clear errors when user starts typing
    const clearFieldError = useCallback((fieldName: string) => {
        setFieldErrors(prev => {
            const newErrors = { ...prev };
            delete newErrors[fieldName];
            return newErrors;
        });
        if (error) setError("");
    }, [error]);

    // Real-time field validation
    const validateField = useCallback((name: string, value: string) => {
        let validation;
        
        switch (name) {
            case 'username':
                validation = SecurityUtils.validateUsername(value);
                break;
            case 'password':
                validation = SecurityUtils.validatePassword(value);
                break;
            case 'otp':
                validation = SecurityUtils.validateOTP(value);
                break;
            default:
                return;
        }
        
        if (!validation.valid && validation.error) {
            setFieldErrors(prev => ({ ...prev, [name]: validation.error! }));
        } else {
            clearFieldError(name);
        }
    }, [clearFieldError]);

    const handleCredentialsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        
        // Rate limiting check
        if (!SecurityUtils.checkRateLimit(lastAttemptRef.current)) {
            setError("Too many attempts. Please wait before trying again.");
            return;
        }

        // Check attempt limit
        if (attemptCountRef.current >= maxAttemptsRef.current) {
            setError("Too many failed attempts. Please try again later.");
            return;
        }

        setError("");
        setFieldErrors({});
        setIsLoading(true);

        try {
            const formData = new FormData(e.currentTarget);
            const rawUsername = formData.get("username");
            const rawPassword = formData.get("password");

            // Type check and sanitization
            if (typeof rawUsername !== "string" || typeof rawPassword !== "string") {
                throw new Error("Invalid input format");
            }

            const username = SecurityUtils.sanitizeInput(rawUsername);
            const password = SecurityUtils.sanitizeInput(rawPassword);

            // Validation
            const usernameValidation = SecurityUtils.validateUsername(username);
            const passwordValidation = SecurityUtils.validatePassword(password);

            const errors: {[key: string]: string} = {};

            if (!usernameValidation.valid) {
                errors.username = usernameValidation.error!;
            }

            if (!passwordValidation.valid) {
                errors.password = passwordValidation.error!;
            }

            if (Object.keys(errors).length > 0) {
                setFieldErrors(errors);
                attemptCountRef.current++;
                return;
            }

            // Record attempt time
            lastAttemptRef.current = Date.now();

            const response = await login({
                username: username,
                password: password
            });

            if (response.success === true) {
                console.log("Login successful");
                // Reset attempt counter on success
                attemptCountRef.current = 0;
                
                if (response.data.user.is_mfa_enabled) {
                    setStage("otp");
                } else {
                    setStage("complete");
                    navigate("/dashboard");
                }
            } else {
                attemptCountRef.current++;
                setError("Invalid credentials. Please try again.");
            }

        } catch (error: any) {
            attemptCountRef.current++;
            console.error("Login error:", error);
            
            // Don't expose internal errors to users
            const userMessage = error.message?.includes("Network") 
                ? "Network error. Please check your connection." 
                : "An error occurred. Please try again.";
            
            setError(userMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleOTPSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        
        // Rate limiting
        if (!SecurityUtils.checkRateLimit(lastAttemptRef.current, 1000)) {
            setError("Please wait before trying again.");
            return;
        }

        setError("");
        setFieldErrors({});
        setIsLoading(true);

        try {
            const formData = new FormData(e.currentTarget);
            const rawOTP = formData.get("otp");

            if (typeof rawOTP !== "string") {
                throw new Error("Invalid OTP format");
            }

            const otp = SecurityUtils.sanitizeInput(rawOTP);
            const otpValidation = SecurityUtils.validateOTP(otp);

            if (!otpValidation.valid) {
                setFieldErrors({ otp: otpValidation.error! });
                return;
            }

            lastAttemptRef.current = Date.now();

            // Use environment variable for base URL
            const baseUri = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

            const response = await fetch(`${baseUri}/auth/verify-otp/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest", // CSRF protection
                },
                credentials: "include",
                body: JSON.stringify({ otp: otp }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log("OTP verification successful");
                navigate("/dashboard");
            } else {
                const errorResponse = await response.json();
                const errorMessage = errorResponse.detail || "Invalid OTP. Please try again.";
                
                // Sanitize error message from server
                setError(SecurityUtils.escapeHtml(errorMessage));
            }

        } catch (err: any) {
            console.error("OTP verification error:", err);
            setError("An error occurred. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="space-y-2 text-center">
                <h1 className="text-2xl font-bold">
                    {stage === "credentials" ? "Login" : "Enter OTP"}
                </h1>
                <p className="text-muted-foreground">
                    {stage === "credentials"
                        ? "Enter your credentials to continue"
                        : "Enter the 6-digit code from your authenticator app"}
                </p>
            </div>

            {error && (
                <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">
                    {error}
                </div>
            )}

            {stage === "credentials" ? (
                <form onSubmit={handleCredentialsSubmit} className="space-y-4" noValidate>
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
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                                fieldErrors.username ? 'border-destructive' : ''
                            }`}
                            placeholder="Enter your username"
                            disabled={isLoading}
                            onChange={(e) => {
                                clearFieldError('username');
                                // Real-time validation with debounce could be added here
                            }}
                            onBlur={(e) => validateField('username', e.target.value)}
                        />
                        {fieldErrors.username && (
                            <p className="text-destructive text-xs">{fieldErrors.username}</p>
                        )}
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
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                                fieldErrors.password ? 'border-destructive' : ''
                            }`}
                            placeholder="Enter your password"
                            disabled={isLoading}
                            onChange={() => clearFieldError('password')}
                            onBlur={(e) => validateField('password', e.target.value)}
                        />
                        {fieldErrors.password && (
                            <p className="text-destructive text-xs">{fieldErrors.password}</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                        disabled={isLoading || Object.keys(fieldErrors).length > 0}
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
                            className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
                                fieldErrors.otp ? 'border-destructive' : ''
                            }`}
                            placeholder="Enter 6-digit code"
                            disabled={isLoading}
                            onChange={() => clearFieldError('otp')}
                            onBlur={(e) => validateField('otp', e.target.value)}
                        />
                        {fieldErrors.otp && (
                            <p className="text-destructive text-xs">{fieldErrors.otp}</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                        disabled={isLoading || Object.keys(fieldErrors).length > 0}
                    >
                        {isLoading ? "Verifying..." : "Verify OTP"}
                    </button>
                </form>
            )}

            {/* Security notice */}
            <div className="text-xs text-muted-foreground text-center">
                <p>Your connection is secure and encrypted</p>
            </div>
        </div>
    );
}