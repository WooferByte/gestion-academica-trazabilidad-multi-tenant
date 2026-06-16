import { TareaEstadoBadge } from "./TareaEstadoBadge";
import type { TareaResponse } from "@/api/types";

interface TareaCardProps {
  tarea: TareaResponse;
  onClick?: () => void;
}

export function TareaCard({ tarea, onClick }: TareaCardProps) {
  return (
    <div
      onClick={onClick}
      className="rounded-lg border border-border bg-surface p-4 cursor-pointer hover:shadow-md transition-shadow space-y-2"
    >
      <div className="flex items-center justify-between">
        <TareaEstadoBadge estado={tarea.estado} />
        <span className="text-xs text-muted-foreground">
          {tarea.created_at
            ? new Date(tarea.created_at).toLocaleDateString("es-AR")
            : ""}
        </span>
      </div>
      <p className="text-sm text-on-surface line-clamp-2">{tarea.descripcion}</p>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span>Asignada por: {tarea.asignado_por_nombre ?? tarea.asignado_por.slice(0, 8)}</span>
        {tarea.comentarios && tarea.comentarios.length > 0 && (
          <span className="ml-auto">{tarea.comentarios.length} comentarios</span>
        )}
      </div>
    </div>
  );
}
