import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { auth } from "@/services/auth";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function MerchantRegistrationForm() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        business_name: "",
        registration_number: "",
        contact_email: "",
        contact_phone: "",
        admin_name: "",
        admin_email: "",
        password: "",
        confirm_password: "",
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (formData.password !== formData.confirm_password) {
            toast.error("Passwords do not match");
            return;
        }

        try {
            await auth.registerMerchant(formData);
            toast.success("Registration successful! Please check your email for verification.");
            navigate("/");
        } catch (error: any) {
            toast.error(error.response?.data?.message || "Registration failed. Please try again.");
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
                <Label htmlFor="business_name">Business Name</Label>
                <Input
                    id="business_name"
                    name="business_name"
                    type="text"
                    required
                    value={formData.business_name}
                    onChange={handleChange}
                    placeholder="Enter your business name"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="registration_number">Registration Number</Label>
                <Input
                    id="registration_number"
                    name="registration_number"
                    type="text"
                    required
                    value={formData.registration_number}
                    onChange={handleChange}
                    placeholder="Enter your business registration number"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="contact_email">Business Email</Label>
                <Input
                    id="contact_email"
                    name="contact_email"
                    type="email"
                    required
                    value={formData.contact_email}
                    onChange={handleChange}
                    placeholder="Enter your business email"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="contact_phone">Business Phone</Label>
                <Input
                    id="contact_phone"
                    name="contact_phone"
                    type="tel"
                    required
                    value={formData.contact_phone}
                    onChange={handleChange}
                    placeholder="Enter your business phone number"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="admin_name">Admin Name</Label>
                <Input
                    id="admin_name"
                    name="admin_name"
                    type="text"
                    required
                    value={formData.admin_name}
                    onChange={handleChange}
                    placeholder="Enter admin's full name"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="admin_email">Admin Email</Label>
                <Input
                    id="admin_email"
                    name="admin_email"
                    type="email"
                    required
                    value={formData.admin_email}
                    onChange={handleChange}
                    placeholder="Enter admin's email"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Create a password"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm Password</Label>
                <Input
                    id="confirm_password"
                    name="confirm_password"
                    type="password"
                    required
                    value={formData.confirm_password}
                    onChange={handleChange}
                    placeholder="Confirm your password"
                />
            </div>

            <Button type="submit" className="w-full">
                Register Merchant
            </Button>
        </form>
    );
} 