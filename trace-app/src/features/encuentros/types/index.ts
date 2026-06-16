export interface SlotFilters {
  materia_id?: string;
}

export interface SlotFormData {
  asignacion_id?: string;
  materia_id: string;
  titulo: string;
  hora: string;
  dia_semana: string;
  fecha_inicio: string;
  cant_semanas: number;
  fecha_unica?: string | null;
  meet_url?: string | null;
}

export interface InstanciaFilters {
  materia_id?: string;
  desde?: string;
  hasta?: string;
  estado?: string;
  slot_id?: string;
  offset?: number;
  limit?: number;
}
