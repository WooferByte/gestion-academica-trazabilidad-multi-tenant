import { useState } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { FilterBar } from "@/features/admin-estructura/shared/FilterBar";
import type { FilterConfig } from "@/features/admin-estructura/shared/FilterBar";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import { useCohortes, useEliminarCohorte } from "../hooks/useCohortes";
import { useCarreras } from "@/features/admin-carreras/hooks/useCarreras";
import { CohorteFormModal } from "../components/CohorteFormModal";
import type { Cohorte } from "../types/cohorte";

export default function AdminCohortesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCohorte, setSelectedCohorte] = useState<Cohorte | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Cohorte | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});

  const { data: carreras } = useCarreras({ activo: true });
  const { data: cohortes, isLoading } = useCohortes({
    carrera_id: filters.carrera_id || undefined,
  });
  const eliminarMutation = useEliminarCohorte();

  const handleEdit = (cohorte: Cohorte) => {
    setSelectedCohorte(cohorte);
    setModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedCohorte(null);
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await eliminarMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedCohorte(null);
  };

  const filterConfigs: FilterConfig[] = [
    {
      key: "carrera_id",
      label: "Carrera",
      type: "select",
      options: carreras?.map((c) => ({ label: c.nombre, value: c.id })) ?? [],
    },
  ];

  const columns = [
    { key: "nombre", header: "Nombre" },
    {
      key: "carrera_id",
      header: "Carrera",
      render: (cohorte: Cohorte) => {
        const carrera = carreras?.find((c) => c.id === cohorte.carrera_id);
        return carrera?.nombre ?? "-";
      },
    },
    {
      key: "anio",
      header: "Año",
      render: (cohorte: Cohorte) => String(cohorte.anio),
    },
    {
      key: "vig_desde",
      header: "Vigencia",
      render: (cohorte: Cohorte) => (
        <span>
          {cohorte.vig_desde} → {cohorte.vig_hasta}
        </span>
      ),
    },
    {
      key: "estado",
      header: "Estado",
      render: (cohorte: Cohorte) => <StatusBadge active={cohorte.activo} />,
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (cohorte: Cohorte) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => handleEdit(cohorte)}>
            Editar
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteTarget(cohorte)}>
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Cohortes" action={{ label: "Nuevo cohorte", onClick: handleCreate }} />

      <FilterBar filters={filterConfigs} onFilter={setFilters} values={filters} />

      <DataTable
        columns={columns}
        data={cohortes ?? []}
        isLoading={isLoading}
        keyExtractor={(item) => item.id}
      />

      <CohorteFormModal
        open={modalOpen}
        onClose={handleModalClose}
        cohorte={selectedCohorte}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar cohorte"
        message={`¿Estás seguro de eliminar el cohorte "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
      />
    </div>
  );
}
