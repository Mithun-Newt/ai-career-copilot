import React from "react";
import { Navigate } from "react-router-dom";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const token = localStorage.getItem("access_token");

  if (!token) {
    // Redirect to login page if token is missing
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
