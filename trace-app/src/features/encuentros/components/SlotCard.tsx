import { Link } from "react-router-dom";
import type { SlotEncuentroResponse } from "@/api/types";

interface SlotCardProps {
  slot: SlotEncuentroResponse;
}

const DIAS_MAP: Record<string, string> = {
  LUNES: "Lunes",
  MARTES: "Martes",
  MIERCOLES: "Miércoles",
  JUEVES: "Jueves",
  VIERNES: "Viernes",
  SABADO: "Sábado",
  DOMINGO: "Domingo",
};

export function SlotCard({ slot }: SlotCardProps) {
  const isRecurrente = slot.cant_semanas > 0;

  return (
    <Link
      to={`/encuentros/slots/${slot.id}`}
      className="block rounded-lg border border-border bg-surface p-4 hover:border-primary/50 transition-colors"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-medium text-on-surface">{slot.titulo}</h3>
          <p className="text-sm text-on-surface-variant mt-1">
            {DIAS_MAP[slot.dia_semana] || slot.dia_semana} - {slot.hora}
          </p>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${isRecurrente ? "bg-primary/10 text-primary" : "bg-surface-variant text-on-surface-variant"}`}>
          {isRecurrente ? `Recurrente (${slot.cant_semanas} sem)` : "Único"}
        </span>
      </div>
      <p className="text-xs text-on-surface-variant mt-2">
        Inicio: {slot.fecha_inicio}
        {slot.meet_url && " · Meet disponible"}
      </p>
    </Link>
  );
}
