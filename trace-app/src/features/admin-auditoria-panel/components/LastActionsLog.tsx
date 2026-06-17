import { DataTable } from "@/features/admin-estructura/shared";
import type { Column } from "@/features/admin-estructura/shared";
import type { LastAction } from "@/features/admin-auditoria-panel/types/auditoria";

type LastActionsLogProps = {
  data?: (LastAction & { usuario_nombre?: string; detalle_texto?: string })[];
  isLoading: boolean;
};

const columns: Column<LastAction & { usuario_nombre?: string; detalle_texto?: string }>[] = [
  {
    key: "fecha_hora",
    header: "Fecha/Hora",
    render: (item) => new Date(item.fecha_hora).toLocaleString(),
  },
  {
    key: "usuario_nombre",
    header: "Usuario",
    render: (item) => item.usuario_nombre ?? item.actor_id.slice(0, 8) + "...",
  },
  { key: "accion", header: "Acción" },
  {
    key: "detalle",
    header: "Detalle",
    render: (item) => (item as Record<string, unknown>).detalle_texto ?? "-",
  },
];

export function LastActionsLog({ data, isLoading }: LastActionsLogProps) {
  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      keyExtractor={(item) => item.id}
      emptyMessage="No hay acciones recientes"
    />
  );
}
