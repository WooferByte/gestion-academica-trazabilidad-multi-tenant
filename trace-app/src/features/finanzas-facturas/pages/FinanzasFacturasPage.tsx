import { useState, useMemo } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { useFacturas, useCrearFactura } from "../hooks/useFacturas";
import { FacturaTable } from "../components/FacturaTable";
import { CrearFacturaDialog } from "../components/CrearFacturaDialog";
import type { CreateFacturaDTO } from "../types/factura";
import type { Factura } from "../types/factura";

export default function FinanzasFacturasPage() {
  const [searchText, setSearchText] = useState("");
  const [crearOpen, setCrearOpen] = useState(false);

  const { data: rawFacturas, isLoading } = useFacturas();
  const crearMutation = useCrearFactura();

  const facturas = useMemo(() => {
    if (!rawFacturas) return [];
    const q = searchText.toLowerCase().trim();
    if (!q) return rawFacturas;
    return (rawFacturas as Factura[]).filter((f) => {
      return (
        f.periodo.toLowerCase().includes(q) ||
        f.detalle.toLowerCase().includes(q) ||
        f.estado.toLowerCase().includes(q)
      );
    });
  }, [rawFacturas, searchText]);

  const handleCrear = (data: CreateFacturaDTO) => {
    crearMutation.mutate(data, {
      onSuccess: () => setCrearOpen(false),
    });
  };

  return (
    <div className="space-y-lg p-lg">
      <PageHeader
        title="Facturas"
        action={{ label: "Nueva factura", onClick: () => setCrearOpen(true) }}
      />

      <input
        type="text"
        placeholder="Buscá por período, detalle o estado..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        className="h-10 w-full rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
      />

      <FacturaTable data={facturas} isLoading={isLoading} />

      <CrearFacturaDialog
        open={crearOpen}
        onClose={() => setCrearOpen(false)}
        onSubmit={handleCrear}
        isPending={crearMutation.isPending}
      />
    </div>
  );
}
