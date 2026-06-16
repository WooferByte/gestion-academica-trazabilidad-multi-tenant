import { useState } from "react";
import type { TurnoFormData } from "@/features/coloquios/types";

interface TurnoFormProps {
  onAdd: (turno: TurnoFormData) => void;
}

export function TurnoForm({ onAdd }: TurnoFormProps) {
  const [fecha, setFecha] = useState("");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [cupo, setCupo] = useState(1);

  const handleClick = () => {
    if (!fecha || !horaInicio || !horaFin) return;

    onAdd({ fecha, hora_inicio: horaInicio, hora_fin: horaFin, cupo });
    setFecha("");
    setHoraInicio("");
    setHoraFin("");
    setCupo(1);
  };

  return (
    <div className="flex flex-wrap gap-3 items-end">
      <div>
        <label className="block text-xs font-medium mb-1">Fecha</label>
        <input
          type="date"
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          className="rounded-md border border-border bg-background px-2 py-1.5 text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Inicio</label>
        <input
          type="time"
          value={horaInicio}
          onChange={(e) => setHoraInicio(e.target.value)}
          className="rounded-md border border-border bg-background px-2 py-1.5 text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Fin</label>
        <input
          type="time"
          value={horaFin}
          onChange={(e) => setHoraFin(e.target.value)}
          className="rounded-md border border-border bg-background px-2 py-1.5 text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Cupo</label>
        <input
          type="number"
          min="1"
          value={cupo}
          onChange={(e) => setCupo(parseInt(e.target.value) || 1)}
          className="rounded-md border border-border bg-background px-2 py-1.5 text-sm w-16"
        />
      </div>
      <button
        type="button"
        onClick={handleClick}
        className="px-3 py-1.5 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
      >
        Agregar
      </button>
    </div>
  );
}
