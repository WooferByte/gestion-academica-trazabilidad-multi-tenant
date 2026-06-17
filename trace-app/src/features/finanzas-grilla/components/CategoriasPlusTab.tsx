import { useState } from "react";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import {
  useCategoriasPlus,
  useCrearCategoriaPlus,
  useActualizarCategoriaPlus,
  useEliminarCategoriaPlus,
  useToggleCategoriaPlus,
} from "../hooks/useGrilla";
import { CategoriaPlusFormModal } from "./CategoriaPlusFormModal";
import type { CategoriaPlus } from "../types/grilla";

export function CategoriasPlusTab() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCat, setSelectedCat] = useState<CategoriaPlus | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<CategoriaPlus | null>(null);

  const { data: categorias, isLoading } = useCategoriasPlus();
  const crearMutation = useCrearCategoriaPlus();
  const actualizarMutation = useActualizarCategoriaPlus();
  const eliminarMutation = useEliminarCategoriaPlus();
  const toggleMutation = useToggleCategoriaPlus();

  const handleCreate = () => {
    setSelectedCat(null);
    setModalOpen(true);
  };

  const handleEdit = (cat: CategoriaPlus) => {
    setSelectedCat(cat);
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await eliminarMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const handleSubmit = (data: { codigo: string; nombre: string; activo?: boolean }) => {
    if (selectedCat) {
      actualizarMutation.mutate(
        { id: selectedCat.id, data },
        { onSuccess: () => setModalOpen(false) },
      );
    } else {
      crearMutation.mutate(data, { onSuccess: () => setModalOpen(false) });
    }
  };

  const columns = [
    { key: "codigo", header: "Código" },
    { key: "nombre", header: "Nombre" },
    {
      key: "activo",
      header: "Estado",
      render: (item: CategoriaPlus) => <StatusBadge active={item.activo} />,
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (item: CategoriaPlus) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => handleEdit(item)}>
            Editar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => toggleMutation.mutate(item.id)}
          >
            {item.activo ? "Desactivar" : "Activar"}
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteTarget(item)}>
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-lg">
      <PageHeader
        title="Categorías Plus"
        action={{ label: "Nueva categoría", onClick: handleCreate }}
      />

      <DataTable
        columns={columns as any}
        data={categorias as any ?? []}
        isLoading={isLoading}
        keyExtractor={(item: any) => item.id}
        emptyMessage="No hay categorías Plus registradas"
      />

      <CategoriaPlusFormModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setSelectedCat(null); }}
        onSubmit={handleSubmit}
        isPending={crearMutation.isPending || actualizarMutation.isPending}
        categoria={selectedCat}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar categoría"
        message={`¿Estás seguro de eliminar la categoría "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
      />
    </div>
  );
}
