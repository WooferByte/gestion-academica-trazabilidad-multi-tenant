export interface AuditLogEntry {
  id: string;
  fecha_hora: string;
  actor_id: string;
  impersonado_id?: string;
  materia_id?: string;
  accion: string;
  detalle?: Record<string, unknown>;
  filas_afectadas: number;
  ip: string;
  user_agent: string;
}

export interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogFilters {
  desde?: string;
  hasta?: string;
  materia_id?: string;
  usuario_id?: string;
  page?: number;
  page_size?: number;
}
