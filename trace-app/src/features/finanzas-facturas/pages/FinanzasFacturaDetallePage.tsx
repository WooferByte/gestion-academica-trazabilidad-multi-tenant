import { useParams, useNavigate } from "react-router-dom";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { Button } from "@/components/ui/Button";
import { useFactura, useCambiarEstadoFactura } from "../hooks/useFacturas";
import { CambiarEstadoFacturaButton } from "../components/CambiarEstadoFacturaButton";

export default function FinanzasFacturaDetallePage() {
  const { facturaId } = useParams<{ facturaId: string }>();
  const navigate = useNavigate();
  const { data: factura, isLoading } = useFactura(facturaId);
  const cambiarEstadoMutation = useCambiarEstadoFactura();

  if (isLoading) {
    return (
      <div className="space-y-lg p-lg">
        <PageHeader title="Factura" />
        <p className="text-gray-500">Cargando...</p>
      </div>
    );
  }

  if (!factura) {
    return (
      <div className="space-y-lg p-lg">
        <PageHeader title="Factura" />
        <p className="text-gray-500">Factura no encontrada</p>
        <Button variant="ghost" onClick={() => navigate("/facturas")}>
          Volver
        </Button>
      </div>
    );
  }

  const handleEstadoChange = (id: string, nuevoEstado: string) => {
    cambiarEstadoMutation.mutate({ id, data: { estado: nuevoEstado } });
  };

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title={`Factura - ${factura.periodo}`} />

      <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Período</p>
            <p className="font-medium">{factura.periodo}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Estado</p>
            <p className="font-medium">
              {factura.estado === "abonada" ? "Abonada" : "Pendiente"}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Detalle</p>
            <p className="font-medium">{factura.detalle}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Cargada</p>
            <p className="font-medium">
              {new Date(factura.cargada_at).toLocaleDateString("es-AR")}
            </p>
          </div>
          {factura.abonada_at && (
            <div>
              <p className="text-sm text-gray-500">Abonada</p>
              <p className="font-medium">
                {new Date(factura.abonada_at).toLocaleDateString("es-AR")}
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-2 pt-4 border-t border-gray-100">
          <CambiarEstadoFacturaButton
            estadoActual={factura.estado}
            facturaId={factura.id}
            onChangeEstado={handleEstadoChange}
            isPending={cambiarEstadoMutation.isPending}
          />
          <Button variant="ghost" onClick={() => navigate("/facturas")}>
            Volver
          </Button>
        </div>
      </div>
    </div>
  );
}
