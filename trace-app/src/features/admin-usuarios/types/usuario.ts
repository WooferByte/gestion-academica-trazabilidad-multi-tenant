export interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  legajo: string | null;
  banco?: string;
  regional: string | null;
  facturador: boolean;
  roles: string[];
  activo: boolean;
  is_active: boolean;
  estado: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateUsuarioDTO {
  nombre: string;
  apellido: string;
  email: string;
  password?: string;
  dni?: string;
  cuil?: string;
  banco?: string;
  cbu?: string;
  alias_cbu?: string;
  regional?: string;
  legajo?: string;
  facturador?: boolean;
}

export interface UpdateUsuarioDTO {
  nombre?: string;
  apellido?: string;
  email?: string;
  dni?: string;
  cuil?: string;
  banco?: string;
  cbu?: string;
  alias_cbu?: string;
  regional?: string;
  legajo?: string;
  facturador?: boolean;
  activo?: boolean;
}

export const PII_FIELDS = ["dni", "cuil", "cbu", "alias_cbu"] as const;
