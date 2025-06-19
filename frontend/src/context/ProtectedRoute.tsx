import { Navigate, Outlet } from "react-router-dom";
import { getAuth } from "@/lib/storage";

interface Props {
    allowedRoles: "admin" | "merchant" | "customer";
}

export const ProtectedRoute = ({ allowedRoles }: Props) => {
    const { user } = getAuth();
    const role = user?.role?.toLowerCase();
    console.log("Auth Exists:", user);
    if (!user) return <Navigate to="/login" />;
    if (!role) return <Navigate to="/unauthorized" />;
    // TEMPORARY FIX: Uncomment the next line to enforce role-based access control
    // BACKEND DOESNT RETURN PROPER ROLES BASED ON FRONTEND TYPES
    // CHECK THIS ISSUE : https://github.com/BLKamau/monochrome/issues/1
    //if (!role || allowedRoles !== role) return <Navigate to="/unauthorized" />;

    return <Outlet />;
};
