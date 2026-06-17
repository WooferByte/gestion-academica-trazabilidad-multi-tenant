export interface Materia {
  id: string;
  codigo: string;
  nombre: string;
  activo: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateMateriaDTO {
  codigo: string;
  nombre: string;
}

export interface UpdateMateriaDTO {
  codigo?: string;
  nombre?: string;
  activo?: boolean;
}
