export interface ConvocatoriaFilters {
  materia_id?: string;
  cohorte_id?: string;
  tipo?: string;
  estado?: string;
  offset?: number;
  limit?: number;
}

export interface TurnoFormData {
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  cupo: number;
}

export interface ConvocatoriaFormData {
  materia_id: string;
  cohorte_id: string;
  instancia: string;
  tipo: string;
  turnos: TurnoFormData[];
}
