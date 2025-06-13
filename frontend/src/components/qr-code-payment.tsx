import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { QRCodeSVG } from "qrcode.react";
import { useState } from "react";
import { Label } from "recharts";

export function PayViaQrCode() {
    const [qrCodeValue, setqrCodeValue] = useState("https://github.com/Goitseone-Themba/phantom-banking");
    const [hasQrChanged, setQrHasChanged] = useState(false);
    const [qrPaymentAmount, setQRPaymentAmount] = useState(0);
    const temporaryEasterEgg = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

    const createQRCodePaymentMethod = function (e: any) {
        e ? e.preventDefault() : null;
        if (qrPaymentAmount === 0 || qrPaymentAmount === null) {
            setQrHasChanged(false);
            setqrCodeValue("https://github.com/Goitseone-Themba/phantom-banking");
            return;
        } else {
            setQrHasChanged(true);
            setqrCodeValue(temporaryEasterEgg);
        }
    };

    return (
        <form onSubmit={createQRCodePaymentMethod}>
            <div className="flex w-[inherit] flex-col gap-6">
                <Card className="w-2xl">
                    <CardHeader>
                        <span className="roboto-heading text-4xl font-bold">Collect Via Qr Code Scan</span>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-row w-auto h-auto">
                            <div className="flex flex-col flex-1 flex-nowrap justify-between">
                                <Label>Amount to be paid.</Label>
                                <Input
                                    required
                                    type="number"
                                    placeholder="Enter amount to be paid"
                                    onChange={(event) => {
                                        if (event.target.value === "") {
                                            setQrHasChanged(false);
                                        } else setQRPaymentAmount(Number(event.target.value));
                                    }}
                                />
                                <Button className="w-auto" onClick={createQRCodePaymentMethod}>
                                    Generate QR CODE
                                </Button>
                            </div>
                            <div className="ml-4">
                                <QRCodeSVG
                                    className={!hasQrChanged ? "opacity-30" : "opacity-100"}
                                    value={qrCodeValue}
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </form>
    );
}
