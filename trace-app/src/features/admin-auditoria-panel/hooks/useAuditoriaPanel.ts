import { useQuery } from "@tanstack/react-query";
import {
  getActionsPerDay,
  getCommsStatus,
  getInteractions,
  getLastActions,
} from "@/features/admin-auditoria-panel/services/auditoria.service";
import type { AuditoriaPanelFilters } from "@/features/admin-auditoria-panel/types/auditoria";

export function useActionsPerDay(filters?: AuditoriaPanelFilters) {
  return useQuery({
    queryKey: ["auditoria", "actions-per-day", filters],
    queryFn: () => getActionsPerDay(filters).then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useCommsStatus(filters?: AuditoriaPanelFilters) {
  return useQuery({
    queryKey: ["auditoria", "comms-status", filters],
    queryFn: () => getCommsStatus(filters).then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useInteractions(filters?: AuditoriaPanelFilters) {
  return useQuery({
    queryKey: ["auditoria", "interactions", filters],
    queryFn: () => getInteractions(filters).then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useLastActions(filters?: AuditoriaPanelFilters) {
  return useQuery({
    queryKey: ["auditoria", "last-actions", filters],
    queryFn: () => getLastActions(filters).then((r) => r.data),
    staleTime: 30 * 1000,
  });
}
