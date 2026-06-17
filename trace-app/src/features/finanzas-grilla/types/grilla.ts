export interface SalarioBase {
  id: string;
  rol: string;
  monto: number;
  desde: string;
  hasta: string | null;
}

export interface SalarioBaseCreateDTO {
  rol: string;
  monto: number;
  desde: string;
}

export interface CategoriaPlus {
  id: string;
  tenant_id: string;
  codigo: string;
  nombre: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface CategoriaPlusCreateDTO {
  codigo: string;
  nombre: string;
  activo?: boolean;
}

export interface CategoriaPlusUpdateDTO {
  codigo?: string;
  nombre?: string;
  activo?: boolean;
}
