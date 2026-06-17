import { useState } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import { useMaterias, useEliminarMateria } from "../hooks/useMaterias";
import { MateriaFormModal } from "../components/MateriaFormModal";
import type { Materia } from "../types/materia";

export default function AdminMateriasPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedMateria, setSelectedMateria] = useState<Materia | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Materia | null>(null);

  const { data: materias, isLoading } = useMaterias();
  const eliminarMutation = useEliminarMateria();

  const handleEdit = (materia: Materia) => {
    setSelectedMateria(materia);
    setModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedMateria(null);
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await eliminarMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedMateria(null);
  };

  const columns = [
    { key: "codigo", header: "Código" },
    { key: "nombre", header: "Nombre" },
    {
      key: "estado",
      header: "Estado",
      render: (materia: Materia) => <StatusBadge active={materia.activo} />,
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (materia: Materia) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => handleEdit(materia)}>
            Editar
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteTarget(materia)}>
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Materias" action={{ label: "Nueva materia", onClick: handleCreate }} />

      <DataTable
        columns={columns}
        data={materias ?? []}
        isLoading={isLoading}
        keyExtractor={(item) => item.id}
      />

      <MateriaFormModal
        open={modalOpen}
        onClose={handleModalClose}
        materia={selectedMateria}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar materia"
        message={`¿Estás seguro de eliminar la materia "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
      />
    </div>
  );
}
