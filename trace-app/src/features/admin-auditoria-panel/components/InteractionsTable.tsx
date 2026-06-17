import { DataTable } from "@/features/admin-estructura/shared";
import type { Column } from "@/features/admin-estructura/shared";
import type { InteractionMetric } from "@/features/admin-auditoria-panel/types/auditoria";

type InteractionsTableProps = {
  data?: (InteractionMetric & { usuario_nombre?: string; materia_nombre?: string })[];
  isLoading: boolean;
  userMap?: Record<string, string>;
  materiaMap?: Record<string, string>;
};

const columns: Column<InteractionMetric & { usuario_nombre?: string; materia_nombre?: string }>[] = [
  {
    key: "usuario_nombre",
    header: "Usuario",
    render: (item) => item.usuario_nombre ?? item.usuario_id.slice(0, 8) + "...",
  },
  {
    key: "materia_nombre",
    header: "Materia",
    render: (item) => item.materia_nombre ?? "-",
  },
  { key: "accion", header: "Acción" },
  { key: "total", header: "Cantidad" },
];

export function InteractionsTable({ data, isLoading }: InteractionsTableProps) {
  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      keyExtractor={(item, index) => `${item.usuario_id}-${item.accion}-${index}`}
      emptyMessage="No hay interacciones registradas"
    />
  );
}
