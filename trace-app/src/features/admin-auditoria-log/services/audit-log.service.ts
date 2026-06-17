import api from "@/api/client";
import type {
  AuditLogResponse,
  AuditLogFilters,
} from "@/features/admin-auditoria-log/types/audit-log";

export function getAuditLog(params?: AuditLogFilters) {
  return api.get<AuditLogResponse>("/auditoria/log", { params });
}
