import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getLiquidaciones,
  calcularLiquidacion,
  cerrarLiquidacion,
  getHistorial,
} from "../services/liquidaciones.service";
import type { CalcularDTO } from "../types/liquidacion";
import { showToast } from "@/components/ui/Toast";

const LIQUIDACIONES_KEY = ["liquidaciones"] as const;
const HISTORIAL_KEY = ["liquidaciones", "historial"] as const;

export function useLiquidaciones(params?: {
  cohorte_id?: string;
  periodo?: string;
  usuario_id?: string;
}) {
  return useQuery({
    queryKey: [...LIQUIDACIONES_KEY, params],
    queryFn: () => getLiquidaciones(params).then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useHistorial(params?: {
  cohorte_id?: string;
  periodo?: string;
  usuario_id?: string;
}) {
  return useQuery({
    queryKey: [...HISTORIAL_KEY, params],
    queryFn: () => getHistorial(params).then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useCalcularLiquidacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CalcularDTO) =>
      calcularLiquidacion(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: LIQUIDACIONES_KEY });
      showToast("Liquidaciones calculadas correctamente", "success");
    },
    onError: () => {
      showToast("Error al calcular liquidaciones", "error");
    },
  });
}

export function useCerrarLiquidacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ cohorteId, periodo }: { cohorteId: string; periodo: string }) =>
      cerrarLiquidacion(cohorteId, periodo).then((r) => r.data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: LIQUIDACIONES_KEY });
      showToast(`${data.cerradas} liquidaciones cerradas para ${data.periodo}`, "success");
    },
    onError: () => {
      showToast("Error al cerrar liquidaciones", "error");
    },
  });
}
