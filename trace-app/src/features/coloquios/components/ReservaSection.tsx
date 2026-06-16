import { useState } from "react";
import { useReservarTurno, useCancelarReserva } from "@/features/coloquios/hooks/useColoquioReservas";
import { showToast } from "@/components/ui/Toast";
import type { TurnoColoquioResponse } from "@/api/types";

interface ReservaSectionProps {
  evaluacionId: string;
  turnos: TurnoColoquioResponse[];
}

export function ReservaSection({ evaluacionId, turnos }: ReservaSectionProps) {
  const [selectedTurnoId, setSelectedTurnoId] = useState("");
  const [reservaId, setReservaId] = useState("");
  const reservarMutation = useReservarTurno();
  const cancelarMutation = useCancelarReserva();

  const handleReservar = async () => {
    if (!selectedTurnoId) {
      showToast("Seleccioná un turno", "warning");
      return;
    }

    try {
      const result = await reservarMutation.mutateAsync({
        evaluacionId,
        data: { turno_id: selectedTurnoId },
      });
      setReservaId(result.id);
      showToast("Reserva creada", "success");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al reservar";
      showToast(msg, "error");
    }
  };

  const handleCancelar = async () => {
    if (!reservaId) return;

    try {
      await cancelarMutation.mutateAsync(reservaId);
      setReservaId("");
      showToast("Reserva cancelada", "success");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al cancelar";
      showToast(msg, "error");
    }
  };

  const turnosDisponibles = turnos.filter((t) => t.cupo - t.ocupados > 0);

  return (
    <div className="space-y-3">
      <h3 className="font-medium">Reserva de Turno</h3>

      {reservaId ? (
        <div className="space-y-2">
          <p className="text-sm text-green-600">Reserva activa: {reservaId}</p>
          <button
            onClick={handleCancelar}
            disabled={cancelarMutation.isPending}
            className="px-4 py-2 text-sm rounded-md border border-destructive text-destructive hover:bg-destructive/10 disabled:opacity-50"
          >
            {cancelarMutation.isPending ? "Cancelando..." : "Cancelar Reserva"}
          </button>
        </div>
      ) : (
        <div className="flex items-end gap-2">
          <div>
            <label className="block text-xs font-medium mb-1">Turno</label>
            <select
              value={selectedTurnoId}
              onChange={(e) => setSelectedTurnoId(e.target.value)}
              className="rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar turno</option>
              {turnosDisponibles.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.fecha} {t.hora_inicio}-{t.hora_fin} (libres: {t.cupo - t.ocupados})
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={handleReservar}
            disabled={reservarMutation.isPending}
            className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {reservarMutation.isPending ? "Reservando..." : "Reservar"}
          </button>
        </div>
      )}
    </div>
  );
}
