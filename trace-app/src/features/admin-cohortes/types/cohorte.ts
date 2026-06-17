export interface Cohorte {
  id: string;
  nombre: string;
  carrera_id: string;
  carrera_nombre?: string;
  anio: number;
  vig_desde: string;
  vig_hasta: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateCohorteDTO {
  nombre: string;
  carrera_id: string;
  anio: number;
  vig_desde: string;
  vig_hasta: string;
}

export interface UpdateCohorteDTO {
  nombre?: string;
  carrera_id?: string;
  anio?: number;
  vig_desde?: string;
  vig_hasta?: string;
  activo?: boolean;
}
