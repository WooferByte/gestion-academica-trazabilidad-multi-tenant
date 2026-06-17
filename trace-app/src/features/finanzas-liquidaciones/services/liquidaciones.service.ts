import api from "@/api/client";
import type { Liquidacion, CalcularDTO, CerrarResponse } from "../types/liquidacion";

export function getLiquidaciones(params?: {
  cohorte_id?: string;
  periodo?: string;
  usuario_id?: string;
}) {
  return api.get<Liquidacion[]>("/liquidaciones", { params });
}

export function calcularLiquidacion(data: CalcularDTO) {
  return api.post<Liquidacion[]>("/liquidaciones/calcular", data);
}

export function cerrarLiquidacion(cohorteId: string, periodo: string) {
  return api.post<CerrarResponse>(`/liquidaciones/cerrar/${cohorteId}/${periodo}`);
}

export function getHistorial(params?: {
  cohorte_id?: string;
  periodo?: string;
  usuario_id?: string;
}) {
  return api.get<Liquidacion[]>("/liquidaciones/historial", { params });
}

export function exportarLiquidaciones(cohorteId: string, periodo: string) {
  return api.get<Blob>("/liquidaciones/exportar", {
    params: { cohorte_id: cohorteId, periodo },
    responseType: "blob",
  });
}
