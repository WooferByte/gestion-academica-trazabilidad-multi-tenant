import { useState, useMemo } from "react";
import { useTodasLasTareas } from "@/features/tareas/hooks/useTareasAdmin";
import { TareasAdminTable } from "@/features/tareas/components/TareasAdminTable";
import { TareasAdminFilters } from "@/features/tareas/components/TareasAdminFilters";
import { Skeleton } from "@/components/ui/Skeleton";

export default function TareasAdminPage() {
  const [filters, setFilters] = useState({
    asignado_a: "",
    asignado_por: "",
    materia_id: "",
    estado: "",
    search: "",
  });

  const queryParams = useMemo(() => {
    const p: Record<string, string> = {};
    if (filters.asignado_a) p.asignado_a = filters.asignado_a;
    if (filters.asignado_por) p.asignado_por = filters.asignado_por;
    if (filters.materia_id) p.materia_id = filters.materia_id;
    if (filters.estado) p.estado = filters.estado;
    if (filters.search) p.search = filters.search;
    return p;
  }, [filters]);

  const { data, isLoading } = useTodasLasTareas(
    Object.keys(queryParams).length > 0 ? queryParams : undefined,
  );

  const items = data?.items ?? [];

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Administración de Tareas
        </h1>
        <span className="text-sm text-muted-foreground">
          {data?.total ?? 0} tareas
        </span>
      </div>

      <div className="rounded-lg border border-border bg-surface p-4">
        <TareasAdminFilters filters={filters} onChange={setFilters} />
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-surface">
          <TareasAdminTable items={items} />
        </div>
      )}
    </div>
  );
}
