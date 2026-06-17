export interface Liquidacion {
  id: string;
  usuario_id: string;
  cohorte_id: string;
  periodo: string;
  rol: string;
  monto_base: number;
  monto_plus: number;
  total: number;
  es_nexo: boolean;
  excluido_por_factura: boolean;
  estado: string;
}

export interface CalcularDTO {
  cohorte_id: string;
  periodo: string;
}

export interface CerrarResponse {
  cerradas: number;
  periodo: string;
}
