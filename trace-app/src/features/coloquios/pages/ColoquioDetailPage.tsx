import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useConvocatoria, useCerrarConvocatoria } from "@/features/coloquios/hooks/useColoquios";
import { AlumnosImportSection } from "@/features/coloquios/components/AlumnosImportSection";
import { ReservaSection } from "@/features/coloquios/components/ReservaSection";
import { ResultadosSection } from "@/features/coloquios/components/ResultadosSection";
import { AgendaSection } from "@/features/coloquios/components/AgendaSection";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";

type TabId = "turnos" | "alumnos" | "resultados" | "agenda";

const TABS: { id: TabId; label: string }[] = [
  { id: "turnos", label: "Turnos" },
  { id: "alumnos", label: "Alumnos" },
  { id: "resultados", label: "Resultados" },
  { id: "agenda", label: "Agenda" },
];

export default function ColoquioDetailPage() {
  const { evaluacionId } = useParams<{ evaluacionId: string }>();
  const navigate = useNavigate();
  const { permissions } = useAuth();
  const isAdmin = permissions.includes("coloquios:gestionar");
  const [activeTab, setActiveTab] = useState<TabId>("turnos");

  const tabs = useMemo(() => {
    if (isAdmin) return TABS;
    return TABS.filter((t) => t.id === "turnos");
  }, [isAdmin]);

  const { data: convocatoria, isLoading } = useConvocatoria(evaluacionId || "");
  const cerrarMutation = useCerrarConvocatoria();

  const handleCerrar = async () => {
    if (!evaluacionId) return;
    if (!window.confirm("¿Estás seguro de cerrar esta convocatoria?")) return;

    try {
      await cerrarMutation.mutateAsync(evaluacionId);
      showToast("Convocatoria cerrada", "success");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al cerrar";
      showToast(msg, "error");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-lg p-lg">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!convocatoria) {
    return (
      <div className="space-y-lg p-lg">
        <p className="text-on-surface-variant">Convocatoria no encontrada</p>
        <button onClick={() => navigate("/coloquios")} className="text-primary text-sm">
          Volver a Coloquios
        </button>
      </div>
    );
  }

  const isActive = convocatoria.estado === "activa";

  return (
    <div className="space-y-lg p-lg">
      <button
        onClick={() => navigate("/coloquios")}
        className="text-sm text-primary hover:underline mb-2 inline-block"
      >
        &larr; Volver a Coloquios
      </button>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-headline-md text-headline-md text-on-surface">
            {convocatoria.instancia}
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {convocatoria.tipo} · Estado: {convocatoria.estado}
          </p>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Convocados: {convocatoria.total_convocados} · Reservas: {convocatoria.reservas_activas} · Cupos libres: {convocatoria.cupos_libres}
          </p>
        </div>
        {isAdmin && isActive && (
          <button
            onClick={handleCerrar}
            disabled={cerrarMutation.isPending}
            className="px-4 py-2 text-sm rounded-md border border-destructive text-destructive hover:bg-destructive/10 disabled:opacity-50"
          >
            {cerrarMutation.isPending ? "Cerrando..." : "Cerrar Convocatoria"}
          </button>
        )}
      </div>

      <div className="border-b border-border">
        <div className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        {activeTab === "turnos" && (
          <div className="space-y-4">
            <h2 className="font-title-md text-title-md">Turnos Disponibles</h2>
            <ReservaSection evaluacionId={evaluacionId || ""} turnos={convocatoria.turnos} />
          </div>
        )}

        {activeTab === "alumnos" && (
          <AlumnosImportSection evaluacionId={evaluacionId || ""} />
        )}

        {activeTab === "resultados" && (
          <ResultadosSection evaluacionId={evaluacionId || ""} />
        )}

        {activeTab === "agenda" && (
          <AgendaSection turnos={convocatoria.turnos} />
        )}
      </div>
    </div>
  );
}
