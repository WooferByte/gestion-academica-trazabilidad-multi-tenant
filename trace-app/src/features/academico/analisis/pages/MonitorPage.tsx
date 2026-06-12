import { useState } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useMonitor } from "@/features/academico/analisis/hooks/useMonitor";
import { MonitorFilters } from "@/features/academico/analisis/components/MonitorFilters";
import { MonitorTable } from "@/features/academico/analisis/components/MonitorTable";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { Skeleton } from "@/components/ui/Skeleton";

export default function MonitorPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { permissions } = useAuth();
  const isCoordinador = permissions.includes("comunicacion:aprobar");
  const [filters, setFilters] = useState({ q: "", fecha_desde: "", fecha_hasta: "" });

  const { data, isLoading } = useMonitor({
    materia_id: materiaId,
    cohorte_id: cohorteId,  // pasamos para que monitor_seguimiento filtre
    q: filters.q || undefined,
    fecha_desde: filters.fecha_desde || undefined,
    fecha_hasta: filters.fecha_hasta || undefined,
  });

  const items = data?.items ?? [];

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

      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Monitor {isCoordinador ? "General" : "de Seguimiento"}
        </h1>
      </div>

      <MonitorFilters filters={filters} onChange={setFilters} showDates={!isCoordinador} />

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <MonitorTable items={items} isGeneral={isCoordinador} />
      )}
    </div>
  );
}
