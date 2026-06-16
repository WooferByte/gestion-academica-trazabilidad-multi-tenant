import { useState } from "react";
import { useAsignaciones, useCrearAsignacion, useActualizarAsignacion, useEliminarAsignacion } from "@/features/equipos/hooks/useAsignaciones";
import { AsignacionTable } from "@/features/equipos/components/AsignacionTable";
import { AsignacionFormDialog } from "@/features/equipos/components/AsignacionFormDialog";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { AsignacionResponse } from "@/api/types";

export default function GestionAsignacionesPage() {
  const [editingItem, setEditingItem] = useState<AsignacionResponse | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const { data, isLoading } = useAsignaciones();
  const crearMutation = useCrearAsignacion();
  const actualizarMutation = useActualizarAsignacion();
  const eliminarMutation = useEliminarAsignacion();

  const items = data?.items ?? [];

  const handleEdit = (item: AsignacionResponse) => {
    setEditingItem(item);
    setIsDialogOpen(true);
  };

  const handleDelete = async (item: AsignacionResponse) => {
    if (window.confirm(`¿Estás seguro de eliminar la asignación de ${item.usuario_nombre || item.usuario_id}?`)) {
      try {
        await eliminarMutation.mutateAsync(item.id);
        showToast("Asignación eliminada correctamente", "success");
      } catch {
        showToast("Error al eliminar la asignación", "error");
      }
    }
  };

  const handleSave = async (data: Record<string, unknown>) => {
    try {
      if (editingItem) {
        await actualizarMutation.mutateAsync({ id: editingItem.id, data });
        showToast("Asignación actualizada correctamente", "success");
      } else {
        await crearMutation.mutateAsync(data as any);
        showToast("Asignación creada correctamente", "success");
      }
      setIsDialogOpen(false);
      setEditingItem(null);
    } catch {
      showToast("Error al guardar la asignación", "error");
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Gestión de Asignaciones
        </h1>
        <button
          onClick={() => {
            setEditingItem(null);
            setIsDialogOpen(true);
          }}
          className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Nueva Asignación
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <AsignacionTable
            items={items}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      )}

      <AsignacionFormDialog
        isOpen={isDialogOpen}
        onClose={() => {
          setIsDialogOpen(false);
          setEditingItem(null);
        }}
        onSave={handleSave}
        initialData={editingItem}
        isPending={crearMutation.isPending || actualizarMutation.isPending}
      />
    </div>
  );
}
