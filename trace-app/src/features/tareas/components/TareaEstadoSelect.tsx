import { useState } from "react";
import { useCambiarEstado } from "@/features/tareas/hooks/useTareas";
import { TareaEstadoBadge } from "./TareaEstadoBadge";
import { showToast } from "@/components/ui/Toast";

interface TareaEstadoSelectProps {
  tareaId: string;
  estadoActual: string;
  estadosPermitidos: string[];
  onCambio?: () => void;
}

const workflowEstados = ["Pendiente", "En progreso", "Resuelta", "Cancelada"];

export function TareaEstadoSelect({ tareaId, estadoActual, estadosPermitidos, onCambio }: TareaEstadoSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const changeMutation = useCambiarEstado();

  const handleChange = (nuevoEstado: string) => {
    changeMutation.mutate(
      { id: tareaId, data: { estado: nuevoEstado } },
      {
        onSuccess: () => {
          showToast("Estado actualizado", "success");
          setIsOpen(false);
          onCambio?.();
        },
        onError: () => {
          showToast("Error al actualizar estado", "error");
        },
      },
    );
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="focus:outline-none"
      >
        <TareaEstadoBadge estado={estadoActual} />
      </button>
      {isOpen && (
        <div className="absolute z-10 mt-1 bg-surface border border-border rounded-md shadow-lg py-1 min-w-[160px]">
          {workflowEstados.map((estado) => {
            const isDisabled = !estadosPermitidos.includes(estado) || estado === estadoActual;
            return (
              <button
                key={estado}
                type="button"
                disabled={isDisabled}
                onClick={() => handleChange(estado)}
                className={`w-full text-left px-3 py-2 text-sm hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed`}
              >
                <TareaEstadoBadge estado={estado} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
