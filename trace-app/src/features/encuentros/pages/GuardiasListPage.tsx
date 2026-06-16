import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useGuardiasList, useActualizarGuardia } from "@/features/encuentros/hooks/useGuardias";
import { ExportCsvButton } from "@/features/encuentros/components/ExportCsvButton";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import type { GuardiaResponse } from "@/api/types";

interface SelectItem {
  id: string;
  nombre: string;
}

function useNameMap(queryKey: string[], url: string): Record<string, string> {
  const { data } = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const res = await api.get(url);
        return (res.data?.items ?? []) as SelectItem[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });
  return useMemo(() => {
    const map: Record<string, string> = {};
    for (const item of data ?? []) map[item.id] = item.nombre;
    return map;
  }, [data]);
}

function resolve(obj: Record<string, string>, key: string | null | undefined, map: Record<string, string>): string {
  if (!key) return "—";
  return map[key] ?? key;
}

const ESTADO_COLORS: Record<string, string> = {
  pendiente: "bg-amber-100 text-amber-800",
  confirmada: "bg-green-100 text-green-800",
  cancelada: "bg-red-100 text-red-800",
};

const ESTADO_LABELS: Record<string, string> = {
  pendiente: "Pendiente",
  confirmada: "Confirmada",
  cancelada: "Cancelada",
};

export default function GuardiasListPage() {
  const [filters, setFilters] = useState({
    materia_id: "",
    carrera_id: "",
    cohorte_id: "",
    estado: "",
  });

  const materiasMap = useNameMap(["materias", "guardias"], "/admin/materias");
  const carrerasMap = useNameMap(["carreras", "guardias"], "/admin/carreras");
  const cohortesMap = useNameMap(["cohortes", "guardias"], "/admin/cohortes");

  const materias = useMemo(() =>
    Object.entries(materiasMap).map(([id, nombre]) => ({ id, nombre })), [materiasMap]);
  const carreras = useMemo(() =>
    Object.entries(carrerasMap).map(([id, nombre]) => ({ id, nombre })), [carrerasMap]);
  const cohortesOption = useMemo(() =>
    Object.entries(cohortesMap).map(([id, nombre]) => ({ id, nombre })), [cohortesMap]);

  const { data, isLoading } = useGuardiasList({
    materia_id: filters.materia_id || undefined,
    carrera_id: filters.carrera_id || undefined,
    cohorte_id: filters.cohorte_id || undefined,
    estado: filters.estado || undefined,
  });

  const updateMutation = useActualizarGuardia();
  const items = data?.items ?? [];

  const handleChangeEstado = async (guardia: GuardiaResponse, nuevoEstado: string) => {
    try {
      await updateMutation.mutateAsync({ id: guardia.id, data: { estado: nuevoEstado } });
      showToast("Estado actualizado", "success");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
      const msg = axiosErr?.response?.data?.detail || axiosErr?.message || "Error al actualizar";
      showToast(msg, "error");
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Guardias
        </h1>
        <ExportCsvButton
          filters={{
            materia_id: filters.materia_id || undefined,
            carrera_id: filters.carrera_id || undefined,
            cohorte_id: filters.cohorte_id || undefined,
            estado: filters.estado || undefined,
          }}
        />
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Materia</label>
          <select
            value={filters.materia_id}
            onChange={(e) => setFilters((f) => ({ ...f, materia_id: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm w-48"
          >
            <option value="">Todas</option>
            {materias.map((m) => (
              <option key={m.id} value={m.id}>{m.nombre}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Carrera</label>
          <select
            value={filters.carrera_id}
            onChange={(e) => setFilters((f) => ({ ...f, carrera_id: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm w-48"
          >
            <option value="">Todas</option>
            {carreras.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Cohorte</label>
          <select
            value={filters.cohorte_id}
            onChange={(e) => setFilters((f) => ({ ...f, cohorte_id: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm w-48"
          >
            <option value="">Todos</option>
            {cohortesOption.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Estado</label>
          <select
            value={filters.estado}
            onChange={(e) => setFilters((f) => ({ ...f, estado: e.target.value }))}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Todos</option>
            <option value="pendiente">Pendiente</option>
            <option value="confirmada">Confirmada</option>
            <option value="cancelada">Cancelada</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="text-on-surface-variant text-center py-12">No hay guardias registradas</p>
      ) : (
        <div className="rounded-lg border border-border bg-surface overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-surface-variant/50">
                <th className="text-left px-4 py-3 font-medium">Día</th>
                <th className="text-left px-4 py-3 font-medium">Horario</th>
                <th className="text-left px-4 py-3 font-medium">Materia</th>
                <th className="text-left px-4 py-3 font-medium">Carrera</th>
                <th className="text-left px-4 py-3 font-medium">Cohorte</th>
                <th className="text-left px-4 py-3 font-medium">Estado</th>
                <th className="text-left px-4 py-3 font-medium">Comentarios</th>
                <th className="text-right px-4 py-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {items.map((guardia) => (
                <tr key={guardia.id} className="hover:bg-surface-variant/30">
                  <td className="px-4 py-3">{guardia.dia}</td>
                  <td className="px-4 py-3">{guardia.horario}</td>
                  <td className="px-4 py-3">{resolve({}, guardia.materia_id, materiasMap)}</td>
                  <td className="px-4 py-3">{resolve({}, guardia.carrera_id, carrerasMap)}</td>
                  <td className="px-4 py-3">{resolve({}, guardia.cohorte_id, cohortesMap)}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${ESTADO_COLORS[guardia.estado] || "bg-gray-100 text-gray-800"}`}>
                      {ESTADO_LABELS[guardia.estado] || guardia.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-on-surface-variant max-w-[200px] truncate">
                    {guardia.comentarios || "-"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <select
                      value={guardia.estado}
                      onChange={(e) => handleChangeEstado(guardia, e.target.value)}
                      className="text-xs rounded border border-border bg-background px-2 py-1"
                    >
                      <option value="pendiente">Pendiente</option>
                      <option value="confirmada">Confirmada</option>
                      <option value="cancelada">Cancelada</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
