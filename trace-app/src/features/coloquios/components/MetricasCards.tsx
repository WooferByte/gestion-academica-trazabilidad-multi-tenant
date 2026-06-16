import type { MetricasColoquiosResponse } from "@/api/types";

interface MetricasCardsProps {
  metricas: MetricasColoquiosResponse | undefined;
  isLoading: boolean;
}

export function MetricasCards({ metricas, isLoading }: MetricasCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-lg border border-border bg-surface p-4 animate-pulse">
            <div className="h-4 w-24 bg-surface-variant rounded mb-2" />
            <div className="h-8 w-16 bg-surface-variant rounded" />
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    { label: "Convocatorias Activas", value: metricas?.total_convocatorias_activas ?? 0, color: "text-blue-600" },
    { label: "Alumnos Convocados", value: metricas?.total_alumnos_convocados ?? 0, color: "text-green-600" },
    { label: "Reservas Activas", value: metricas?.total_reservas_activas ?? 0, color: "text-amber-600" },
    { label: "Resultados Registrados", value: metricas?.total_resultados_registrados ?? 0, color: "text-purple-600" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-lg border border-border bg-surface p-4">
          <p className="text-sm text-on-surface-variant">{card.label}</p>
          <p className={`text-3xl font-bold mt-1 ${card.color}`}>
            {card.value.toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}
