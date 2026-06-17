import { useQuery } from "@tanstack/react-query";
import { getAuditLog } from "@/features/admin-auditoria-log/services/audit-log.service";
import type { AuditLogFilters } from "@/features/admin-auditoria-log/types/audit-log";

export function useAuditLog(filters: AuditLogFilters) {
  return useQuery({
    queryKey: ["auditoria", "log", filters],
    queryFn: () =>
      getAuditLog(filters).then((r) => {
        const items = Array.isArray(r.data) ? r.data : r.data?.items ?? [];
        return {
          items,
          total: filters.page_size ? items.length : items.length,
          page: filters.page ?? 1,
          page_size: filters.page_size ?? (items.length || 1),
        };
      }),
    staleTime: 30 * 1000,
    placeholderData: (prev) => prev,
  });
}
