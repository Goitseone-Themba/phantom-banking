import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

interface Props {
  allowedRoles: ("admin" | "merchant" | "customer")[];
}

export const ProtectedRoute = ({ allowedRoles }: Props) => {
  const { isAuthenticated, userRole } = useAuth();

  if (!isAuthenticated) return <Navigate to="/login" />;
  if (userRole && !allowedRoles.includes(userRole)) return <Navigate to="/unauthorized" />;

  return <Outlet />;
};
