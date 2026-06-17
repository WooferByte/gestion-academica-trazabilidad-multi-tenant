export interface Factura {
  id: string;
  usuario_id: string;
  periodo: string;
  detalle: string;
  referencia_archivo: string | null;
  tamano_kb: number | null;
  estado: string;
  cargada_at: string;
  abonada_at: string | null;
}

export interface CreateFacturaDTO {
  usuario_id: string;
  periodo: string;
  detalle: string;
  referencia_archivo?: string | null;
  tamano_kb?: number | null;
}

export interface CambioEstadoDTO {
  estado: string;
}
