export interface ActionsPerDay {
  fecha: string;
  accion: string;
  total: number;
}

export interface CommsStatus {
  usuario_id: string;
  docente_email: string | null;
  pendientes: number;
  enviadas: number;
  fallidas: number;
}

export interface InteractionMetric {
  usuario_id: string;
  materia_id: string | null;
  accion: string;
  total: number;
}

export interface LastAction {
  id: string;
  fecha_hora: string;
  actor_id: string;
  accion: string;
  detalle?: Record<string, unknown>;
}

export interface AuditoriaPanelFilters {
  desde?: string;
  hasta?: string;
  materia_id?: string;
  usuario_id?: string;
  estado?: string;
  limit?: number;
}
