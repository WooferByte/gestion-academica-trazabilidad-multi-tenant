import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/features/auth/hooks/useAuth";

type ProtectedRouteProps = {
  requiredPermission?: string | string[];
  fallbackPath?: string;
};

export function ProtectedRoute({
  requiredPermission,
  fallbackPath = "/login",
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, permissions } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={fallbackPath} replace />;
  }

  if (requiredPermission) {
    const required = Array.isArray(requiredPermission)
      ? requiredPermission
      : [requiredPermission];
    const hasAccess = required.every((p) => permissions.includes(p));

    if (!hasAccess) {
      return (
        <div className="flex h-screen flex-col items-center justify-center gap-md bg-background">
          <h1 className="font-headline-lg text-headline-lg text-on-surface">
            403
          </h1>
          <p className="font-body-lg text-body-lg text-secondary">
            Sin permisos suficientes
          </p>
          <p className="font-body-md text-body-md text-on-surface-variant">
            No tenés acceso a esta sección
          </p>
        </div>
      );
    }
  }

  return <Outlet />;
}
