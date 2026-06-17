import api from "@/api/client";
import type { Factura, CreateFacturaDTO, CambioEstadoDTO } from "../types/factura";

export function getFacturas() {
  return api.get<Factura[]>("/facturas", { params: { _t: Date.now() } });
}

export function getFactura(id: string) {
  return api.get<Factura>(`/facturas/${id}`);
}

export function createFactura(data: CreateFacturaDTO) {
  return api.post<Factura>("/facturas", data);
}

export function cambiarEstadoFactura(id: string, data: CambioEstadoDTO) {
  return api.patch<Factura>(`/facturas/${id}/estado`, data);
}
