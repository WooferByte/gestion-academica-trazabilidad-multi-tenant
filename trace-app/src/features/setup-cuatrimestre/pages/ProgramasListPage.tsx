import { useState, useMemo } from "react";
import {
  useProgramasList,
  useCrearPrograma,
  useActualizarPrograma,
  useEliminarPrograma,
} from "@/features/setup-cuatrimestre/hooks/useProgramas";
import { SelectorCarreraCohorte } from "@/features/setup-cuatrimestre/components/SelectorCarreraCohorte";
import { ProgramaForm } from "@/features/setup-cuatrimestre/components/ProgramaForm";
import { ProgramaTable } from "@/features/setup-cuatrimestre/components/ProgramaTable";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { ProgramaMateriaResponse } from "@/api/types";

export default function ProgramasListPage() {
  const [carreraId, setCarreraId] = useState("");
  const [cohorteId, setCohorteId] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<ProgramaMateriaResponse | null>(null);

  const { data, isLoading } = useProgramasList();
  const createMutation = useCrearPrograma();
  const updateMutation = useActualizarPrograma();
  const deleteMutation = useEliminarPrograma();

  const items = useMemo(() => {
    if (!data?.items) return [];
    return data.items.filter((p) => {
      if (carreraId && p.carrera_id !== carreraId) return false;
      if (cohorteId && p.cohorte_id !== cohorteId) return false;
      return true;
    });
  }, [data, carreraId, cohorteId]);

  const handleSave = async (formData: {
    materia_id: string;
    carrera_id: string;
    cohorte_id: string;
    titulo: string;
  }) => {
    try {
      if (editItem) {
        await updateMutation.mutateAsync({
          id: editItem.id,
          data: { titulo: formData.titulo },
        });
        showToast("Programa actualizado", "success");
      } else {
        await createMutation.mutateAsync(formData);
        showToast("Programa creado", "success");
      }
      setShowForm(false);
      setEditItem(null);
    } catch {
      showToast("Error al guardar el programa", "error");
    }
  };

  const handleEdit = (item: ProgramaMateriaResponse) => {
    setEditItem(item);
    setShowForm(true);
  };

  const handleDelete = (item: ProgramaMateriaResponse) => {
    if (window.confirm(`¿Estás seguro de eliminar "${item.titulo}"?`)) {
      deleteMutation.mutate(item.id, {
        onSuccess: () => showToast("Programa eliminado", "success"),
        onError: () => showToast("Error al eliminar", "error"),
      });
    }
  };

  return (
    <div className="space-y-lg">
      <div className="flex items-center justify-between">
        <h2 className="font-headline-sm text-headline-sm text-on-surface">
          Programas de Materia
        </h2>
        {!showForm && (
          <button
            type="button"
            onClick={() => {
              setEditItem(null);
              setShowForm(true);
            }}
            className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Nuevo Programa
          </button>
        )}
      </div>

      <div className="rounded-lg border border-border bg-surface p-4">
        <SelectorCarreraCohorte
          carreraId={carreraId}
          cohorteId={cohorteId}
          onCarreraChange={setCarreraId}
          onCohorteChange={setCohorteId}
        />
      </div>

      {showForm && (
        <div className="rounded-lg border border-border bg-surface p-6">
          <ProgramaForm
            onSave={handleSave}
            onCancel={() => { setShowForm(false); setEditItem(null); }}
            editItem={editItem ?? undefined}
            carreraId={carreraId || undefined}
            cohorteId={cohorteId || undefined}
            isSubmitting={createMutation.isPending || updateMutation.isPending}
          />
        </div>
      )}

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <ProgramaTable
            items={items}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      )}
    </div>
  );
}
