import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "@/features/auth/hooks/useAuth";
import { ProtectedRoute } from "@/components/routing/ProtectedRoute";
import { PublicRoute } from "@/components/routing/PublicRoute";
import { LoadingSkeleton } from "@/components/routing/LoadingSkeleton";
import { AppLayout } from "@/features/shell/components/AppLayout";
import { ToastContainer } from "@/components/ui/Toast";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";

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
const MisEquiposPage = lazy(() => import("@/features/equipos/pages/MisEquiposPage"));
const GestionAsignacionesPage = lazy(() => import("@/features/equipos/pages/GestionAsignacionesPage"));
const AsignacionMasivaPage = lazy(() => import("@/features/equipos/pages/AsignacionMasivaPage"));
const ClonarEquipoPage = lazy(() => import("@/features/equipos/pages/ClonarEquipoPage"));
const VigenciaPage = lazy(() => import("@/features/equipos/pages/VigenciaPage"));
const AvisosListPage = lazy(() => import("@/features/avisos/pages/AvisosListPage"));
const AvisoFormPage = lazy(() => import("@/features/avisos/pages/AvisoFormPage"));
const AvisosActivosPage = lazy(() => import("@/features/avisos/pages/AvisosActivosPage"));

// Encuentros
const EncuentroSlotsListPage = lazy(() => import("@/features/encuentros/pages/EncuentroSlotsListPage"));
const EncuentroSlotCrearPage = lazy(() => import("@/features/encuentros/pages/EncuentroSlotCrearPage"));
const EncuentroSlotDetailPage = lazy(() => import("@/features/encuentros/pages/EncuentroSlotDetailPage"));
const GuardiasListPage = lazy(() => import("@/features/encuentros/pages/GuardiasListPage"));

// Coloquios
const ColoquiosDashboardPage = lazy(() => import("@/features/coloquios/pages/ColoquiosDashboardPage"));
const ColoquioCrearPage = lazy(() => import("@/features/coloquios/pages/ColoquioCrearPage"));
const ColoquioDetailPage = lazy(() => import("@/features/coloquios/pages/ColoquioDetailPage"));
const MetricasColoquiosPage = lazy(() => import("@/features/coloquios/pages/MetricasColoquiosPage"));

// Tareas
const TareasPage = lazy(() => import("@/features/tareas/pages/TareasPage"));
const TareaDetailPage = lazy(() => import("@/features/tareas/pages/TareaDetailPage"));

// Finanzas
const FinanzasLiquidacionesPage = lazy(() => import("@/features/finanzas-liquidaciones/pages/FinanzasLiquidacionesPage"));
const FinanzasLiquidacionesHistorialPage = lazy(() => import("@/features/finanzas-liquidaciones/pages/FinanzasLiquidacionesHistorialPage"));
const FinanzasFacturasPage = lazy(() => import("@/features/finanzas-facturas/pages/FinanzasFacturasPage"));
const FinanzasFacturaDetallePage = lazy(() => import("@/features/finanzas-facturas/pages/FinanzasFacturaDetallePage"));
const FinanzasGrillaPage = lazy(() => import("@/features/finanzas-grilla/pages/FinanzasGrillaPage"));

// Setup Cuatrimestre
const SetupCuatrimestrePage = lazy(() => import("@/features/setup-cuatrimestre/pages/SetupCuatrimestrePage"));

// Admin pages
const AdminCarrerasPage = lazy(() => import("@/features/admin-carreras/pages/AdminCarrerasPage"));
const AdminCohortesPage = lazy(() => import("@/features/admin-cohortes/pages/AdminCohortesPage"));
const AdminMateriasPage = lazy(() => import("@/features/admin-materias/pages/AdminMateriasPage"));
const AdminUsuariosPage = lazy(() => import("@/features/admin-usuarios/pages/AdminUsuariosPage"));
const AdminAuditoriaPanelPage = lazy(() => import("@/features/admin-auditoria-panel/pages/AdminAuditoriaPanelPage"));
const AdminAuditoriaLogPage = lazy(() => import("@/features/admin-auditoria-log/pages/AdminAuditoriaLogPage"));

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
              <Route path="equipos">
                <Route index element={<SuspenseWrapper><MisEquiposPage /></SuspenseWrapper>} />
                <Route path="asignaciones" element={<SuspenseWrapper><GestionAsignacionesPage /></SuspenseWrapper>} />
                <Route path="asignacion-masiva" element={<SuspenseWrapper><AsignacionMasivaPage /></SuspenseWrapper>} />
                <Route path="clonar" element={<SuspenseWrapper><ClonarEquipoPage /></SuspenseWrapper>} />
                <Route path="vigencia" element={<SuspenseWrapper><VigenciaPage /></SuspenseWrapper>} />
              </Route>
              <Route path="avisos">
                <Route index element={<SuspenseWrapper><AvisosListPage /></SuspenseWrapper>} />
                <Route path="crear" element={<SuspenseWrapper><AvisoFormPage /></SuspenseWrapper>} />
                <Route path="editar/:id" element={<SuspenseWrapper><AvisoFormPage /></SuspenseWrapper>} />
                <Route path="activos" element={<SuspenseWrapper><AvisosActivosPage /></SuspenseWrapper>} />
              </Route>
              <Route path="encuentros">
                <Route index element={<SuspenseWrapper><EncuentroSlotsListPage /></SuspenseWrapper>} />
                <Route path="crear" element={<SuspenseWrapper><EncuentroSlotCrearPage /></SuspenseWrapper>} />
                <Route path="slots/:slotId" element={<SuspenseWrapper><EncuentroSlotDetailPage /></SuspenseWrapper>} />
                <Route path="guardias" element={<SuspenseWrapper><GuardiasListPage /></SuspenseWrapper>} />
              </Route>
              <Route path="coloquios">
                <Route index element={<SuspenseWrapper><ColoquiosDashboardPage /></SuspenseWrapper>} />
                <Route path="crear" element={<SuspenseWrapper><ColoquioCrearPage /></SuspenseWrapper>} />
                <Route path="metricas" element={<SuspenseWrapper><MetricasColoquiosPage /></SuspenseWrapper>} />
                <Route path=":evaluacionId" element={<SuspenseWrapper><ColoquioDetailPage /></SuspenseWrapper>} />
              </Route>
              <Route path="tareas">
                <Route index element={<SuspenseWrapper><TareasPage /></SuspenseWrapper>} />
                <Route path=":tareaId" element={<SuspenseWrapper><TareaDetailPage /></SuspenseWrapper>} />
              </Route>
              <Route path="liquidaciones">
                <Route index element={<SuspenseWrapper><FinanzasLiquidacionesPage /></SuspenseWrapper>} />
                <Route path="historial" element={<SuspenseWrapper><FinanzasLiquidacionesHistorialPage /></SuspenseWrapper>} />
              </Route>
              <Route path="facturas">
                <Route index element={<SuspenseWrapper><FinanzasFacturasPage /></SuspenseWrapper>} />
                <Route path=":facturaId" element={<SuspenseWrapper><FinanzasFacturaDetallePage /></SuspenseWrapper>} />
              </Route>
              <Route path="finanzas/grilla">
                <Route index element={<SuspenseWrapper><FinanzasGrillaPage /></SuspenseWrapper>} />
              </Route>
              <Route path="setup-cuatrimestre">
                <Route index element={<SuspenseWrapper><SetupCuatrimestrePage /></SuspenseWrapper>} />
              </Route>
              <Route path="admin">
                <Route path="carreras" element={<SuspenseWrapper><ErrorBoundary><AdminCarrerasPage /></ErrorBoundary></SuspenseWrapper>} />
                <Route path="cohortes" element={<SuspenseWrapper><ErrorBoundary><AdminCohortesPage /></ErrorBoundary></SuspenseWrapper>} />
                <Route path="materias" element={<SuspenseWrapper><ErrorBoundary><AdminMateriasPage /></ErrorBoundary></SuspenseWrapper>} />
                <Route path="usuarios" element={<SuspenseWrapper><ErrorBoundary><AdminUsuariosPage /></ErrorBoundary></SuspenseWrapper>} />
                <Route path="auditoria">
                  <Route index element={<SuspenseWrapper><ErrorBoundary><AdminAuditoriaPanelPage /></ErrorBoundary></SuspenseWrapper>} />
                  <Route path="log" element={<SuspenseWrapper><ErrorBoundary><AdminAuditoriaLogPage /></ErrorBoundary></SuspenseWrapper>} />
                </Route>
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
