import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "@/features/auth/hooks/useAuth";
import { ProtectedRoute } from "@/components/routing/ProtectedRoute";
import { PublicRoute } from "@/components/routing/PublicRoute";
import { LoadingSkeleton } from "@/components/routing/LoadingSkeleton";
import { AppLayout } from "@/features/shell/components/AppLayout";
import { ToastContainer } from "@/components/ui/Toast";

const LoginPage = lazy(() => import("@/features/auth/pages/LoginPage"));
const TwoFactorPage = lazy(() => import("@/features/auth/pages/TwoFactorPage"));
const RecoveryPage = lazy(() => import("@/features/auth/pages/RecoveryPage"));
const DashboardPage = lazy(() => import("@/features/shell/pages/DashboardPage"));
const NotFoundPage = lazy(() => import("@/components/routing/NotFoundPage"));

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingSkeleton />}>{children}</Suspense>;
}

export function RouterProvider() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="login" element={<SuspenseWrapper><LoginPage /></SuspenseWrapper>} />
            <Route path="login/2fa" element={<SuspenseWrapper><TwoFactorPage /></SuspenseWrapper>} />
            <Route path="recovery" element={<SuspenseWrapper><RecoveryPage /></SuspenseWrapper>} />
          </Route>
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<SuspenseWrapper><DashboardPage /></SuspenseWrapper>} />
            </Route>
          </Route>
          <Route path="*" element={<SuspenseWrapper><NotFoundPage /></SuspenseWrapper>} />
        </Routes>
        <ToastContainer />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default RouterProvider;
