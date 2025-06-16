import { useState } from "react";
export function ForgotPassword() {
    const [isLoading, setIsLoading] = useState<boolean>(false);

    function sendForgotPasswordRequest(e: React.FormEvent<HTMLFormElement>) {
        const data = new FormData(e.currentTarget);
        e.preventDefault();
        setIsLoading(true);

        fetch("/api/v1/auth/forgot-password/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: data.get("email"),
            }),
        })
            .then((response) => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Failed to send reset password email.");
                }
            })
            .catch((err) => {
                throw new Error(err.message);
            })
            .finally(() => {
                setIsLoading(false);
            });
    }
    return (
        <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
            <h1 className="text-2xl font-bold mb-4">Forgot Password</h1>
            <p className="mb-6">Please enter your email to reset your password.</p>
            <form className="w-full max-w-sm" onSubmit={sendForgotPasswordRequest}>
                <input
                    type="email"
                    placeholder="Email"
                    className="w-full p-2.5 mb-4 border border-gray-300 rounded"
                    required
                />
                <button
                    type="submit"
                    className={` ${
                        isLoading
                            ? "opacity-90 bg-red-200 cursor-not-allowed pointer-none:"
                            : "w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                    }`}
                >
                    Reset Password
                </button>
            </form>
        </div>
    );
}
