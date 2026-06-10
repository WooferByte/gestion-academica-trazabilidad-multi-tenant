import { useParams } from "react-router-dom";
import { useComisionKPIs } from "@/features/academico/comision/hooks/useComisionKPIs";
import { KpiCard } from "@/features/academico/comision/components/KpiCard";
import { ActionMenu } from "@/features/academico/comision/components/ActionMenu";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";

const KPI_CONFIG = [
  { title: "Total alumnos", icon: "people", key: "total_alumnos" as const },
  { title: "Actividades", icon: "assignment", key: "total_actividades" as const },
  { title: "Aprobados", icon: "check_circle", key: "alumnos_aprobados" as const },
  { title: "Atrasados", icon: "warning", key: "alumnos_atrasados" as const },
  { title: "Promedio", icon: "trending_up", key: "promedio_general" as const },
];

export default function ComisionDashboardPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const { data, isLoading, isError, error } = useComisionKPIs(materiaId!, cohorteId!);
  const breadcrumb = useBreadcrumb();

  return (
    <div className="space-y-lg p-lg">
      <nav className="flex items-center gap-xs font-body-sm text-body-sm text-on-surface-variant">
        {breadcrumb.map((b, i) => (
          <span key={i} className="flex items-center gap-xs">
            {i > 0 && <span className="material-symbols-outlined text-[16px]">chevron_right</span>}
            {b.path ? (
              <a href={b.path} className="hover:text-primary transition-colors">{b.label}</a>
            ) : (
              <span className="text-on-surface">{b.label}</span>
            )}
          </span>
        ))}
      </nav>

      {isError && (
        <div className="rounded-lg bg-error-container p-md font-body-sm text-body-sm text-on-error-container">
          Error al cargar indicadores: {(error as Error)?.message ?? "Error desconocido"}
        </div>
      )}

      <div className="grid grid-cols-2 gap-md md:grid-cols-3 lg:grid-cols-5">
        {KPI_CONFIG.map((kpi) => (
          <KpiCard
            key={kpi.key}
            title={kpi.title}
            icon={kpi.icon}
            value={data?.[kpi.key] ?? null}
            loading={isLoading}
          />
        ))}
      </div>

      <ActionMenu />
    </div>
  );
}
