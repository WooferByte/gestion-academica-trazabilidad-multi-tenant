import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { showToast } from "@/components/ui/Toast";
import {
  getFacturas,
  getFactura,
  createFactura,
  cambiarEstadoFactura,
} from "../services/facturas.service";
import type { CreateFacturaDTO, CambioEstadoDTO } from "../types/factura";

export function useFacturas() {
  const [mountKey] = useState(() => Date.now());
  return useQuery({
    queryKey: ["facturas", mountKey],
    queryFn: () => getFacturas().then((r) => r.data),
    staleTime: 0,
    gcTime: 0,
  });
}

export function useFactura(id: string | undefined) {
  return useQuery({
    queryKey: ["facturas", id],
    queryFn: () => getFactura(id!).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCrearFactura() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateFacturaDTO) => createFactura(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["facturas"] });
      showToast("Factura creada correctamente", "success");
    },
    onError: () => {
      showToast("Error al crear la factura", "error");
    },
  });
}

export function useCambiarEstadoFactura() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CambioEstadoDTO }) =>
      cambiarEstadoFactura(id, data).then((r) => r.data),
    onSuccess: () => {
      qc.resetQueries({ queryKey: ["facturas"] });
      showToast("Estado actualizado correctamente", "success");
    },
    onError: (err) => {
      const msg = err instanceof Error ? err.message : "Error al cambiar el estado";
      showToast(msg, "error");
    },
  });
}
