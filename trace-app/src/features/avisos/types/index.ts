export interface AvisoFilters {
  activo?: boolean;
  alcance?: string;
  desde?: string;
  hasta?: string;
}

export interface AvisoFormData {
  alcance: string;
  materia_id?: string;
  cohorte_id?: string;
  rol_destino?: string;
  severidad: string;
  titulo: string;
  cuerpo: string;
  inicio_vigencia: string;
  fin_vigencia: string;
  orden: number;
  requiere_ack: boolean;
}
