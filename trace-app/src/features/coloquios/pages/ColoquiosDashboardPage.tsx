import { useNavigate } from "react-router-dom";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { useMetricas, useConvocatoriasList } from "@/features/coloquios/hooks/useColoquios";
import { MetricasCards } from "@/features/coloquios/components/MetricasCards";
import { ConvocatoriaTable } from "@/features/coloquios/components/ConvocatoriaTable";

export default function ColoquiosDashboardPage() {
  const navigate = useNavigate();
  const { permissions } = useAuth();
  const isAdmin = permissions.includes("coloquios:gestionar");
  const { data: metricas, isLoading: metricasLoading } = useMetricas(isAdmin);
  const { data: convocatoriasData, isLoading: convLoading } = useConvocatoriasList();

  const convocatorias = convocatoriasData?.items ?? [];

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Coloquios
        </h1>
        {isAdmin && (
          <button
            onClick={() => navigate("/coloquios/crear")}
            className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Nueva Convocatoria
          </button>
        )}
      </div>

      <MetricasCards metricas={metricas} isLoading={metricasLoading} />

      <div>
        <h2 className="font-title-md text-title-md text-on-surface mb-4">
          Convocatorias ({convocatorias.length})
        </h2>
        {convLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-12 bg-surface-variant/50 animate-pulse rounded" />
            ))}
          </div>
        ) : (
          <ConvocatoriaTable items={convocatorias} />
        )}
      </div>
    </div>
  );
}
