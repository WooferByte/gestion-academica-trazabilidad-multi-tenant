import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useSlot } from "@/features/encuentros/hooks/useEncuentrosSlots";
import { useInstanciasList, useEditarInstancia } from "@/features/encuentros/hooks/useEncuentrosInstancias";
import { InstanciaRow } from "@/features/encuentros/components/InstanciaRow";
import { InstanciaEditModal } from "@/features/encuentros/components/InstanciaEditModal";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { InstanciaEncuentroResponse, InstanciaEncuentroUpdate } from "@/api/types";

export default function EncuentroSlotDetailPage() {
  const { slotId } = useParams<{ slotId: string }>();
  const navigate = useNavigate();

  const { data: slot, isLoading: slotLoading } = useSlot(slotId || "");
  const { data: instanciasData, isLoading: instanciasLoading } = useInstanciasList(
    slotId ? { slot_id: slotId } : {}
  );

  const editMutation = useEditarInstancia();
  const [editingInstancia, setEditingInstancia] = useState<InstanciaEncuentroResponse | null>(null);

  const instancias = instanciasData?.items ?? [];

  const handleEditSave = async (id: string, data: InstanciaEncuentroUpdate) => {
    try {
      await editMutation.mutateAsync({ id, data });
      showToast("Instancia actualizada", "success");
      setEditingInstancia(null);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al actualizar";
      showToast(msg, "error");
    }
  };

  if (slotLoading) {
    return (
      <div className="space-y-lg p-lg">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (!slot) {
    return (
      <div className="space-y-lg p-lg">
        <p className="text-on-surface-variant">Slot no encontrado</p>
        <button onClick={() => navigate("/encuentros")} className="text-primary text-sm">
          Volver a Encuentros
        </button>
      </div>
    );
  }

  const DIAS_MAP: Record<string, string> = {
    LUNES: "Lunes", MARTES: "Martes", MIERCOLES: "Miércoles",
    JUEVES: "Jueves", VIERNES: "Viernes", SABADO: "Sábado",
  };

  return (
    <div className="space-y-lg p-lg">
      <div>
        <button
          onClick={() => navigate("/encuentros")}
          className="text-sm text-primary hover:underline mb-4 inline-block"
        >
          &larr; Volver a Encuentros
        </button>

        <h1 className="font-headline-md text-headline-md text-on-surface">
          {slot.titulo}
        </h1>
        <p className="text-sm text-on-surface-variant mt-1">
          {DIAS_MAP[slot.dia_semana] || slot.dia_semana} - {slot.hora}hs
          {slot.cant_semanas > 0 && ` · Recurrente (${slot.cant_semanas} semanas)`}
          {slot.meet_url && " · Meet disponible"}
        </p>
        <p className="text-xs text-on-surface-variant mt-1">
          Inicio: {slot.fecha_inicio}
        </p>
      </div>

      <div>
        <h2 className="font-title-md text-title-md text-on-surface mb-4">
          Instancias ({instancias.length})
        </h2>

        {instanciasLoading ? (
          <div className="space-y-sm">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : instancias.length === 0 ? (
          <p className="text-on-surface-variant text-sm py-8 text-center">
            No hay instancias generadas para este slot
          </p>
        ) : (
          <div className="rounded-lg border border-border bg-surface divide-y divide-border">
            {instancias.map((instancia) => (
              <InstanciaRow
                key={instancia.id}
                instancia={instancia}
                onEdit={setEditingInstancia}
              />
            ))}
          </div>
        )}
      </div>

      <InstanciaEditModal
        instancia={editingInstancia}
        isOpen={!!editingInstancia}
        onClose={() => setEditingInstancia(null)}
        onSave={handleEditSave}
        isPending={editMutation.isPending}
      />
    </div>
  );
}
