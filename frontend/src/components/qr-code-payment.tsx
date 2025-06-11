import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";

export function PayViaQrCode() {
    const [qrCodeValue, setqrCodeValue] = useState("https://github.com/Goitseone-Themba/phantom-banking/");
    const [hasQrChanged, setQrHasChanged] = useState(false);
    const [qrPaymentAmount, setQRPaymentAmount] = useState("");

    const createQRCodePaymentMethod = function () {
        // USE THE qrPaymentAmount Value To Generate A QRCODE
        // qrPaymentAmount -> Use This in IRL VERSION
        setQrHasChanged(true);
        setqrCodeValue("https://www.youtube.com/watch?v=dQw4w9WgXcQ");
    };

    return (
        <div className="flex w-[inherit] flex-col gap-6">
            <Card className="w-2xl">
                <CardHeader>
                    <h2 className="roboto-heading text-4xl font-bold">Collect Via Qr Code Scan</h2>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-row w-auto h-auto">
                        <div className="flex flex-col flex-1 flex-nowrap justify-between">
                            <Input
                                type="number"
                                placeholder="Enter amount to be paid"
                                onChange={(event) => {
                                    console.log(event.target.value);
                                    if (event.target.value !== "") {
                                        setQRPaymentAmount(event.target.value);
                                    }
                                }}
                                onKeyUp={(event) => {
                                    console.log(event.code);
                                    if (event.code === "Enter") {
                                        createQRCodePaymentMethod();
                                    }
                                }}
                            />
                            <Button className="w-auto" onClick={createQRCodePaymentMethod}>
                                Generate QR CODE
                            </Button>
                        </div>
                        <div className="ml-4">
                            <QRCodeSVG
                                className={!hasQrChanged ? "opacity-50" : "opacity-100"}
                                aria-disabled={!hasQrChanged}
                                value={qrCodeValue}
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
