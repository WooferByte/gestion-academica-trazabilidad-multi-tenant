import { useState } from "react";
import { useMisEquipos } from "@/features/equipos/hooks/useMisEquipos";
import { AsignacionTable } from "@/features/equipos/components/AsignacionTable";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { Skeleton } from "@/components/ui/Skeleton";

export default function MisEquiposPage() {
  const { permissions } = useAuth();
  const isCoordinador = permissions.includes("equipos:asignar");
  const [filters, setFilters] = useState({
    materia_id: "",
    cohorte_id: "",
    solo_vigentes: true,
  });

  const { data, isLoading } = useMisEquipos(
    filters.materia_id || filters.cohorte_id
      ? {
          materia_id: filters.materia_id || undefined,
          cohorte_id: filters.cohorte_id || undefined,
          solo_vigentes: filters.solo_vigentes,
        }
      : { solo_vigentes: filters.solo_vigentes },
  );

  const items = data?.items ?? [];

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          {isCoordinador ? "Gestión de Equipos" : "Mis Equipos"}
        </h1>
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Materia</label>
          <input
            value={filters.materia_id}
            onChange={(e) => setFilters((f) => ({ ...f, materia_id: e.target.value }))}
            placeholder="Filtrar por materia"
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Cohorte</label>
          <input
            value={filters.cohorte_id}
            onChange={(e) => setFilters((f) => ({ ...f, cohorte_id: e.target.value }))}
            placeholder="Filtrar por cohorte"
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
        <div className="flex items-center gap-2 pb-1">
          <input
            type="checkbox"
            id="solo-vigentes"
            checked={filters.solo_vigentes}
            onChange={(e) => setFilters((f) => ({ ...f, solo_vigentes: e.target.checked }))}
          />
          <label htmlFor="solo-vigentes" className="text-sm">
            Solo vigentes
          </label>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <AsignacionTable items={items} />
        </div>
      )}
    </div>
  );
}
