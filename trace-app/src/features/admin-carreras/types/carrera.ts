export interface Carrera {
  id: string;
  codigo: string;
  nombre: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateCarreraDTO {
  codigo: string;
  nombre: string;
}

export interface UpdateCarreraDTO {
  codigo?: string;
  nombre?: string;
  activo?: boolean;
}
