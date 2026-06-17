import api from "@/api/client";
import type {
  ActionsPerDay,
  CommsStatus,
  InteractionMetric,
  LastAction,
  AuditoriaPanelFilters,
} from "@/features/admin-auditoria-panel/types/auditoria";

export function getActionsPerDay(params?: AuditoriaPanelFilters) {
  return api.get<ActionsPerDay[]>("/auditoria/acciones-por-dia", { params });
}

export function getCommsStatus(params?: AuditoriaPanelFilters) {
  return api.get<CommsStatus[]>("/auditoria/comunicaciones-por-docente", { params });
}

export function getInteractions(params?: AuditoriaPanelFilters) {
  return api.get<InteractionMetric[]>("/auditoria/interacciones-por-docente-materia", { params });
}

export function getLastActions(params?: AuditoriaPanelFilters) {
  return api.get<LastAction[]>("/auditoria/log", { params });
}
