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
const ComisionSelectorPage = lazy(() => import("@/features/academico/comision/pages/ComisionSelectorPage"));
const ComisionDashboardPage = lazy(() => import("@/features/academico/comision/pages/ComisionDashboardPage"));
const ImportarPage = lazy(() => import("@/features/academico/importacion/pages/ImportarPage"));
const UmbralPage = lazy(() => import("@/features/academico/analisis/pages/UmbralPage"));
const AtrasadosPage = lazy(() => import("@/features/academico/analisis/pages/AtrasadosPage"));
const RankingPage = lazy(() => import("@/features/academico/analisis/pages/RankingPage"));
const NotasFinalesPage = lazy(() => import("@/features/academico/analisis/pages/NotasFinalesPage"));
const TpsSinCorregirPage = lazy(() => import("@/features/academico/analisis/pages/TpsSinCorregirPage"));
const ComunicarPage = lazy(() => import("@/features/academico/comunicaciones/pages/ComunicarPage"));
const MonitorPage = lazy(() => import("@/features/academico/analisis/pages/MonitorPage"));

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
              <Route
                path="academico"
                element={<ProtectedRoute />}
              >
                <Route index element={<SuspenseWrapper><ComisionSelectorPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId" element={<SuspenseWrapper><ComisionDashboardPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/importar" element={<SuspenseWrapper><ImportarPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/umbral" element={<SuspenseWrapper><UmbralPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/atrasados" element={<SuspenseWrapper><AtrasadosPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/ranking" element={<SuspenseWrapper><RankingPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/notas" element={<SuspenseWrapper><NotasFinalesPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/tps-sin-corregir" element={<SuspenseWrapper><TpsSinCorregirPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/comunicar" element={<SuspenseWrapper><ComunicarPage /></SuspenseWrapper>} />
                <Route path=":materiaId/:cohorteId/monitor" element={<SuspenseWrapper><MonitorPage /></SuspenseWrapper>} />
              </Route>
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
