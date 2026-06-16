import { useNavigate } from "react-router-dom";
import { useMetricas } from "@/features/coloquios/hooks/useColoquios";
import { MetricasCards } from "@/features/coloquios/components/MetricasCards";

export default function MetricasColoquiosPage() {
  const navigate = useNavigate();
  const { data: metricas, isLoading } = useMetricas();

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Métricas de Coloquios
        </h1>
        <button
          onClick={() => navigate("/coloquios")}
          className="px-4 py-2 text-sm rounded-md border border-border hover:bg-surface-variant"
        >
          Ver Convocatorias
        </button>
      </div>

      <MetricasCards metricas={metricas} isLoading={isLoading} />
    </div>
  );
}
