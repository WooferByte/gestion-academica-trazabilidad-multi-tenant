import { useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  PageHeader,
  FilterBar,
  DataTable,
  EmptyState,
} from "@/features/admin-estructura/shared";
import type { Column, FilterConfig } from "@/features/admin-estructura/shared";
import api from "@/api/client";
import { useAuditLog } from "@/features/admin-auditoria-log/hooks/useAuditLog";
import type { AuditLogEntry } from "@/features/admin-auditoria-log/types/audit-log";

const PAGE_SIZE = 25;

export default function AdminAuditoriaLogPage() {
  const [filterValues, setFilterValues] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);

  const filtersForApi = {
    desde: filterValues.desde || undefined,
    hasta: filterValues.hasta || undefined,
    materia_id: filterValues.materia_id || undefined,
    usuario_id: filterValues.usuario_id || undefined,
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading } = useAuditLog(filtersForApi);
  const hasActiveFilters = Object.values(filterValues).some((v) => v !== "");

  const handleFilter = useCallback((values: Record<string, string>) => {
    setFilterValues(values);
    setPage(1);
  }, []);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;
  const isEmpty = !isLoading && (!data || data.items.length === 0);

  // Load users and materias for name lookup
  const { data: usuarios } = useQuery({
    queryKey: ["usuarios", "all"],
    queryFn: () => api.get<{ items: Array<{ id: string; nombre: string; apellido: string; email: string }> }>("/admin/usuarios").then((r) => r.data.items),
    staleTime: 5 * 60 * 1000,
  });

  const userMap = useMemo(() => {
    const map: Record<string, string> = {};
    usuarios?.forEach((u) => { map[u.id] = `${u.nombre} ${u.apellido}`.trim() || u.email; });
    return map;
  }, [usuarios]);

  const filters: FilterConfig[] = [
    { key: "desde", label: "Desde", type: "date" },
    { key: "hasta", label: "Hasta", type: "date" },
    { key: "materia_id", label: "Materia ID", type: "text" },
    { key: "usuario_id", label: "Usuario ID", type: "text" },
  ];

  const columns: Column<AuditLogEntry>[] = [
    { key: "fecha_hora", header: "Fecha/Hora", render: (item) => new Date(item.fecha_hora).toLocaleString() },
    {
      key: "actor_id",
      header: "Usuario",
      render: (item) => userMap[item.actor_id] ?? item.actor_id.slice(0, 8) + "...",
    },
    {
      key: "materia_id",
      header: "Materia",
      render: (item) => item.materia_id ? item.materia_id.slice(0, 8) + "..." : "-",
    },
    { key: "accion", header: "Acción" },
    { key: "filas_afectadas", header: "Reg. Afectados" },
    { key: "ip", header: "IP Origen" },
    {
      key: "user_agent",
      header: "User Agent",
      render: (item) => (
        <span className="text-body-sm text-on-surface-variant truncate max-w-[200px] block" title={item.user_agent}>
          {item.user_agent}
        </span>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-6 p-lg">
      <PageHeader title="Registro de Auditoría" />

      <FilterBar
        filters={filters}
        onFilter={handleFilter}
        values={filterValues}
      />

      {isEmpty && !hasActiveFilters && (
        <EmptyState message="No hay registros de auditoría disponibles" />
      )}

      {isEmpty && hasActiveFilters && (
        <EmptyState message="No se encontraron registros para los filtros seleccionados" />
      )}

      {!isEmpty && (
        <DataTable
          columns={columns}
          data={data?.items ?? []}
          isLoading={isLoading}
          page={page}
          pageSize={PAGE_SIZE}
          totalPages={totalPages}
          onPageChange={setPage}
          keyExtractor={(item) => item.id}
          emptyMessage="No se encontraron registros"
        />
      )}
    </div>
  );
}
