import { useNavigate } from "react-router-dom";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { Button } from "@/components/ui/Button";
import type { Factura } from "../types/factura";

type FacturaTableProps = {
  data: Factura[];
  isLoading: boolean;
};

export function FacturaTable({ data, isLoading }: FacturaTableProps) {
  const navigate = useNavigate();

  const columns = [
    { key: "periodo", header: "Período" },
    {
      key: "detalle",
      header: "Detalle",
      render: (item: Factura) => (
        <span className="max-w-xs truncate block">{item.detalle}</span>
      ),
    },
    {
      key: "estado",
      header: "Estado",
      render: (item: Factura) => {
        const esAbonada = item.estado?.toLowerCase() === "abonada";
        return <StatusBadge active={esAbonada} label={esAbonada ? "Abonada" : "Pendiente"} />;
      },
    },
    {
      key: "cargada_at",
      header: "Cargada",
      render: (item: Factura) => new Date(item.cargada_at).toLocaleDateString("es-AR"),
    },
    {
      key: "acciones",
      header: "Acciones",
      render: (item: Factura) => (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/facturas/${item.id}`)}
        >
          Ver detalle
        </Button>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns as any}
      data={data as any}
      isLoading={isLoading}
      keyExtractor={(item: any) => item.id}
      emptyMessage="No se encontraron facturas"
    />
  );
}
