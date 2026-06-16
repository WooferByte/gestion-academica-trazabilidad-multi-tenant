import type { TurnoColoquioResponse } from "@/api/types";
import type { TurnoFormData } from "@/features/coloquios/types";

interface TurnoListProps {
  turnos: TurnoColoquioResponse[] | TurnoFormData[];
  onRemove?: (index: number) => void;
  isEditable?: boolean;
}

export function TurnoList({ turnos, onRemove, isEditable }: TurnoListProps) {
  if (turnos.length === 0) {
    return <p className="text-sm text-on-surface-variant py-4">No hay turnos agregados</p>;
  }

  return (
    <div className="space-y-2">
      {turnos.map((turno, idx) => {
        const isBackend = "id" in turno;
        return (
          <div key={isBackend ? (turno as TurnoColoquioResponse).id : idx} className="flex items-center justify-between py-2 px-3 rounded-md bg-surface-variant/30">
            <div>
              <p className="text-sm font-medium">
                {turno.fecha} · {turno.hora_inicio} - {turno.hora_fin}
              </p>
              <p className="text-xs text-on-surface-variant">
                Cupo: {turno.cupo}
                {isBackend && ` · Ocupados: ${(turno as TurnoColoquioResponse).ocupados}`}
              </p>
            </div>
            {isEditable && onRemove && (
              <button
                onClick={() => onRemove(idx)}
                className="text-xs px-2 py-1 rounded border border-destructive text-destructive hover:bg-destructive/10"
              >
                Quitar
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
