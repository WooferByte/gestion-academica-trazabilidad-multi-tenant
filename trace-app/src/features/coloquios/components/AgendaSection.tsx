import type { TurnoColoquioResponse } from "@/api/types";

interface AgendaSectionProps {
  turnos: TurnoColoquioResponse[];
}

export function AgendaSection({ turnos }: AgendaSectionProps) {
  if (turnos.length === 0) {
    return <p className="text-sm text-on-surface-variant py-4">No hay turnos en esta convocatoria</p>;
  }

  const sorted = [...turnos].sort((a, b) => `${a.fecha}T${a.hora_inicio}`.localeCompare(`${b.fecha}T${b.hora_inicio}`));

  return (
    <div className="space-y-3">
      <h3 className="font-medium">Agenda de Turnos</h3>

      <div className="space-y-3">
        {sorted.map((turno) => {
          const ocupacionPct = turno.cupo > 0 ? Math.round((turno.ocupados / turno.cupo) * 100) : 0;
          return (
            <div key={turno.id} className="rounded-lg border border-border bg-surface p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="font-medium text-sm">
                    {turno.fecha} · {turno.hora_inicio} - {turno.hora_fin}
                  </p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${ocupacionPct >= 100 ? "bg-red-100 text-red-800" : ocupacionPct >= 75 ? "bg-amber-100 text-amber-800" : "bg-green-100 text-green-800"}`}>
                  {turno.ocupados}/{turno.cupo} ocupados
                </span>
              </div>

              <div className="w-full bg-surface-variant rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${ocupacionPct >= 100 ? "bg-red-500" : ocupacionPct >= 75 ? "bg-amber-500" : "bg-green-500"}`}
                  style={{ width: `${Math.min(ocupacionPct, 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
