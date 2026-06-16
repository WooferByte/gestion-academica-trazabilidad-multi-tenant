import type { InstanciaEncuentroResponse } from "@/api/types";

interface InstanciaRowProps {
  instancia: InstanciaEncuentroResponse;
  onEdit: (instancia: InstanciaEncuentroResponse) => void;
}

const ESTADO_COLORS: Record<string, string> = {
  pendiente: "bg-amber-100 text-amber-800",
  realizado: "bg-green-100 text-green-800",
  cancelado: "bg-red-100 text-red-800",
};

const ESTADO_LABELS: Record<string, string> = {
  pendiente: "Pendiente",
  realizado: "Realizado",
  cancelado: "Cancelado",
};

export function InstanciaRow({ instancia, onEdit }: InstanciaRowProps) {
  const stateColor = ESTADO_COLORS[instancia.estado] || "bg-gray-100 text-gray-800";
  const stateLabel = ESTADO_LABELS[instancia.estado] || instancia.estado;

  return (
    <div className="flex items-center justify-between py-2 px-3 rounded-md hover:bg-surface-variant/50 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm text-on-surface">{instancia.titulo}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${stateColor}`}>
            {stateLabel}
          </span>
        </div>
        <p className="text-xs text-on-surface-variant mt-0.5">
          {instancia.fecha} - {instancia.hora}
          {instancia.meet_url && " · Meet ✓"}
          {instancia.video_url && " · Video ✓"}
        </p>
      </div>
      <button
        onClick={() => onEdit(instancia)}
        className="text-xs px-3 py-1 rounded-md border border-border hover:bg-surface-variant transition-colors"
      >
        Editar
      </button>
    </div>
  );
}
