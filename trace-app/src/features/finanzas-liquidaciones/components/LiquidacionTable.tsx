import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { Button } from "@/components/ui/Button";
import type { Liquidacion } from "../types/liquidacion";

type LiquidacionTableProps = {
  data: Liquidacion[];
  isLoading: boolean;
  userMap?: Record<string, string>;
  mostrarAcciones?: boolean;
  onExportar?: (item: Liquidacion) => void;
};

export function LiquidacionTable({ data, isLoading, userMap = {}, mostrarAcciones = true, onExportar }: LiquidacionTableProps) {
  const columns = [
    { key: "periodo", header: "Período" },
    {
      key: "usuario_id",
      header: "Usuario",
      render: (item: Liquidacion) => userMap[item.usuario_id] ?? item.usuario_id.slice(0, 8) + "...",
    },
    { key: "rol", header: "Rol" },
    {
      key: "monto_base",
      header: "Monto Base",
      render: (item: Liquidacion) => `$${item.monto_base.toFixed(2)}`,
    },
    {
      key: "monto_plus",
      header: "Monto Plus",
      render: (item: Liquidacion) => `$${item.monto_plus.toFixed(2)}`,
    },
    {
      key: "total",
      header: "Total",
      render: (item: Liquidacion) => `$${item.total.toFixed(2)}`,
    },
    {
      key: "estado",
      header: "Estado",
      render: (item: Liquidacion) => <StatusBadge active={item.estado?.toLowerCase() === "cerrada"} label={item.estado} />,
    },
    ...(mostrarAcciones
      ? [
          {
            key: "acciones",
            header: "Acciones",
            render: (item: Liquidacion) => (
              <div className="flex gap-2">
                {onExportar && (
                  <Button variant="secondary" size="sm" onClick={() => onExportar(item)}>
                    Exportar
                  </Button>
                )}
              </div>
            ),
          },
        ]
      : []),
  ];

  return (
    <DataTable
      columns={columns as any}
      data={data as any}
      isLoading={isLoading}
      keyExtractor={(item: any) => item.id}
    />
  );
}
