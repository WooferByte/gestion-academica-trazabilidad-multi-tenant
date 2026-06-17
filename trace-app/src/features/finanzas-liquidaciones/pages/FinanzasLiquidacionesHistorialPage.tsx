import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import api from "@/api/client";
import { useHistorial } from "../hooks/useLiquidaciones";
import { LiquidacionTable } from "../components/LiquidacionTable";

export default function FinanzasLiquidacionesHistorialPage() {

  const { data: rawHistorial, isLoading } = useHistorial();

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

  const historial = useMemo(() => {
    if (!rawHistorial) return [];
    const q = searchText.toLowerCase().trim();
    if (!q) return rawHistorial;
    return rawHistorial.filter((l) => {
      const userName = userMap[l.usuario_id]?.toLowerCase() ?? "";
      return (
        l.periodo.toLowerCase().includes(q) ||
        l.rol.toLowerCase().includes(q) ||
        l.estado.toLowerCase().includes(q) ||
        userName.includes(q)
      );
    });
  }, [rawHistorial, searchText, userMap]);

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Historial de Liquidaciones" />

      <input
        type="text"
        placeholder="Buscá por período, rol, estado o usuario..."
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        className="h-10 w-full rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
      />

      <LiquidacionTable
        data={historial}
        isLoading={isLoading}
        userMap={userMap}
        mostrarAcciones={false}
      />
    </div>
  );
}
