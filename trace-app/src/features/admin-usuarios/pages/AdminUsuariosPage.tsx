import { useState } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { FilterBar } from "@/features/admin-estructura/shared/FilterBar";
import type { FilterConfig } from "@/features/admin-estructura/shared/FilterBar";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { Button } from "@/components/ui/Button";
import { useUsuarios, useEliminarUsuario } from "../hooks/useUsuarios";
import { UsuarioFormModal } from "../components/UsuarioFormModal";
import type { Usuario } from "../types/usuario";

export default function AdminUsuariosPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedUsuario, setSelectedUsuario] = useState<Usuario | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Usuario | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});

  const { data: usuarios, isLoading } = useUsuarios({
    activo: filters.estado ? filters.estado === "activo" : undefined,
  });
  const eliminarMutation = useEliminarUsuario();

  const handleEdit = (usuario: Usuario) => {
    setSelectedUsuario(usuario);
    setModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedUsuario(null);
    setModalOpen(true);
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await eliminarMutation.mutateAsync(deleteTarget.id);
    setDeleteTarget(null);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedUsuario(null);
  };

  const filterConfigs: FilterConfig[] = [
    {
      key: "estado",
      label: "Estado",
      type: "select",
      options: [
        { label: "Activo", value: "activo" },
        { label: "Inactivo", value: "inactivo" },
      ],
    },
  ];

  const columns = [
    {
      key: "nombre_completo",
      header: "Nombre",
      render: (usuario: Usuario) => `${usuario.nombre} ${usuario.apellido}`.trim(),
    },
    { key: "email", header: "Email" },
    { key: "legajo", header: "Legajo", render: (usuario: Usuario) => usuario.legajo ?? "-" },
    {
      key: "roles",
      header: "Rol",
      render: (usuario: Usuario) => usuario.roles?.join(", ") ?? "-",
    },
    {
      key: "estado",
      header: "Estado",
      render: (usuario: Usuario) => <StatusBadge active={usuario.activo} />,
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (usuario: Usuario) => (
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => handleEdit(usuario)}>
            Editar
          </Button>
          <Button variant="danger" size="sm" onClick={() => setDeleteTarget(usuario)}>
            Eliminar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Usuarios" action={{ label: "Nuevo usuario", onClick: handleCreate }} />

      <FilterBar filters={filterConfigs} onFilter={setFilters} values={filters} />

      <DataTable
        columns={columns}
        data={usuarios ?? []}
        isLoading={isLoading}
        keyExtractor={(item) => item.id}
      />

      <UsuarioFormModal
        open={modalOpen}
        onClose={handleModalClose}
        usuario={selectedUsuario}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        title="Eliminar usuario"
        message={`¿Estás seguro de eliminar el usuario "${deleteTarget?.nombre} ${deleteTarget?.apellido}"?`}
        confirmLabel="Eliminar"
      />
    </div>
  );
}
