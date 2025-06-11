import { LoginForm } from "@/components/login-form";

export function Login() {
    return (
        <>
            <div className="grid min-h-svh lg:grid-cols-2">
                <div className="bg-muted relative hidden lg:block  justify-center">
                    <img
                        src="../../src/assets/phantom-banking.svg"
                        alt="Image"
                        className="justify-self-center inset-0 object-cover dark:brightness-[0.2] dark:grayscale"
                    />
                </div>
                <div className="flex flex-col gap-4 p-6 md:p-10">
                    <div className="flex flex-1 items-center justify-center">
                        <div className="w-full max-w-xs">
                            <LoginForm />
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
