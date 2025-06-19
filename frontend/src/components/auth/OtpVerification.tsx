import React from "react";
import { Label } from "../ui/label";
import { Input } from "../ui/input";

export function LoginVerifyViaOtp() {
    const [otpCode, setOTPCode] = React.useState("");
    const verifyOTPCode = (e) => {
        fetch("")
            .then((res) => {
                if (res.ok) {
                }
            })
            .catch((e) => {});
    };
    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                verifyOTPCode(e);
            }}
        >
            <div className="flex flex-nowrap flex-col gap-6 p-6">
                <h1>Hello Please Verify Your OTP Code.</h1>
                <Label>OTP Code</Label>
                <Input
                    value={otpCode}
                    onChange={(e) => {
                        setOTPCode(e.target.value);
                    }}
                ></Input>
            </div>
        </form>
    );
}
