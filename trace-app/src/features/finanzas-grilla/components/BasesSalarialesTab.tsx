import { useState } from "react";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { useBases, useCrearBase } from "../hooks/useGrilla";
import { SalarioBaseFormModal } from "./SalarioBaseFormModal";
import type { SalarioBase } from "../types/grilla";

export function BasesSalarialesTab() {
  const [modalOpen, setModalOpen] = useState(false);
  const { data: bases, isLoading } = useBases();
  const crearMutation = useCrearBase();

  const columns = [
    {
      key: "rol",
      header: "Rol",
      render: (item: SalarioBase) => {
        const labels: Record<string, string> = {
          PROFESOR: "Profesor",
          TUTOR: "Tutor",
          NEXO: "Nexo",
          COORDINADOR: "Coordinador",
        };
        return labels[item.rol] ?? item.rol;
      },
    },
    {
      key: "monto",
      header: "Monto",
      render: (item: SalarioBase) =>
        new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(item.monto),
    },
    {
      key: "desde",
      header: "Vigencia desde",
      render: (item: SalarioBase) => new Date(item.desde).toLocaleDateString("es-AR"),
    },
    {
      key: "hasta",
      header: "Vigencia hasta",
      render: (item: SalarioBase) =>
        item.hasta ? new Date(item.hasta).toLocaleDateString("es-AR") : "Vigente",
    },
  ];

  return (
    <div className="space-y-lg">
      <PageHeader
        title="Bases Salariales"
        action={{ label: "Nueva base", onClick: () => setModalOpen(true) }}
      />

      <DataTable
        columns={columns as any}
        data={bases as any ?? []}
        isLoading={isLoading}
        keyExtractor={(item: any) => item.id}
        emptyMessage="No hay bases salariales registradas"
      />

      <SalarioBaseFormModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={(data) =>
          crearMutation.mutate(data, { onSuccess: () => setModalOpen(false) })
        }
        isPending={crearMutation.isPending}
      />
    </div>
  );
}
