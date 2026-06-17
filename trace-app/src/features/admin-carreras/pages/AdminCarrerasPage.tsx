import { useState } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import { useCarreras, useEliminarCarrera } from "../hooks/useCarreras";
import { CarreraFormModal } from "../components/CarreraFormModal";
import type { Carrera } from "../types/carrera";

export default function AdminCarrerasPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCarrera, setSelectedCarrera] = useState<Carrera | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Carrera | null>(null);

  const { data: carreras, isLoading } = useCarreras();
  const eliminarMutation = useEliminarCarrera();

  const handleEdit = (carrera: Carrera) => {
    setSelectedCarrera(carrera);
    setModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedCarrera(null);
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await eliminarMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedCarrera(null);
  };

  const columns = [
    { key: "codigo", header: "Código" },
    { key: "nombre", header: "Nombre" },
    {
      key: "estado",
      header: "Estado",
      render: (carrera: Carrera) => <StatusBadge active={carrera.activo} />,
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (carrera: Carrera) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => handleEdit(carrera)}>
            Editar
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteTarget(carrera)}>
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Carreras" action={{ label: "Nueva carrera", onClick: handleCreate }} />

      <DataTable
        columns={columns}
        data={carreras ?? []}
        isLoading={isLoading}
        keyExtractor={(item) => item.id}
      />

      <CarreraFormModal
        open={modalOpen}
        onClose={handleModalClose}
        carrera={selectedCarrera}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar carrera"
        message={`¿Estás seguro de eliminar la carrera "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
      />
    </div>
  );
}
