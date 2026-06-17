import { useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { Button } from "@/components/ui/Button";
import api from "@/api/client";
import { useLiquidaciones } from "../hooks/useLiquidaciones";
import { LiquidacionTable } from "../components/LiquidacionTable";
import { CalcularLiquidacionDialog } from "../components/CalcularLiquidacionDialog";
import { CerrarLiquidacionDialog } from "../components/CerrarLiquidacionDialog";
import { exportarLiquidaciones } from "../services/liquidaciones.service";
import { showToast } from "@/components/ui/Toast";
import type { Liquidacion } from "../types/liquidacion";

export default function FinanzasLiquidacionesPage() {
  const navigate = useNavigate();
  const [calcularOpen, setCalcularOpen] = useState(false);
  const [cerrarOpen, setCerrarOpen] = useState(false);

  const { data: rawLiquidaciones, isLoading } = useLiquidaciones();

  const { data: usuarios } = useQuery({
    queryKey: ["usuarios", "all"],
    queryFn: () => api.get<{ items: Array<{ id: string; nombre: string; apellido: string }> }>("/admin/usuarios").then((r) => r.data.items),
    staleTime: 5 * 60 * 1000,
  });

  const userMap = useMemo(() => {
    const map: Record<string, string> = {};
    usuarios?.forEach((u) => { map[u.id] = `${u.nombre} ${u.apellido}`.trim(); });
    return map;
  }, [usuarios]);

  const [searchText, setSearchText] = useState("");

  const liquidaciones = useMemo(() => {
    if (!rawLiquidaciones) return [];
    const q = searchText.toLowerCase().trim();
    if (!q) return rawLiquidaciones;
    return rawLiquidaciones.filter((l) => {
      const userName = userMap[l.usuario_id]?.toLowerCase() ?? "";
      return (
        l.periodo.toLowerCase().includes(q) ||
        l.rol.toLowerCase().includes(q) ||
        l.estado.toLowerCase().includes(q) ||
        userName.includes(q)
      );
    });
  }, [rawLiquidaciones, searchText, userMap]);

  const handleExportar = useCallback(async (item: Liquidacion) => {
    try {
      const response = await exportarLiquidaciones(item.cohorte_id, item.periodo);
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `liquidaciones-${item.cohorte_id}-${item.periodo}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      showToast("Archivo exportado correctamente", "success");
    } catch {
      showToast("Error al exportar liquidaciones", "error");
    }
  }, []);

  return (
    <div className="space-y-lg p-lg">
      <PageHeader
        title="Liquidaciones"
        action={{ label: "Historial", onClick: () => navigate("/liquidaciones/historial") }}
      />

      <div className="flex flex-wrap gap-md">
        <Button variant="primary" onClick={() => setCalcularOpen(true)}>
          Calcular
        </Button>
        <Button variant="secondary" onClick={() => setCerrarOpen(true)}>
          Cerrar
        </Button>
      </div>

      <input
        type="text"
        placeholder="Buscá por período, rol, estado o usuario..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        className="h-10 w-full rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
      />

      <LiquidacionTable
        data={liquidaciones}
        isLoading={isLoading}
        userMap={userMap}
        onExportar={handleExportar}
      />

      <CalcularLiquidacionDialog
        open={calcularOpen}
        onClose={() => setCalcularOpen(false)}
      />

      <CerrarLiquidacionDialog
        open={cerrarOpen}
        onClose={() => setCerrarOpen(false)}
      />
    </div>
  );
}
