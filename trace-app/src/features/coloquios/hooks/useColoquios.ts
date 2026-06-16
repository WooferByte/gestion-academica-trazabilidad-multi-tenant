import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  obtenerMetricas,
  listarConvocatorias,
  obtenerConvocatoria,
  crearConvocatoria,
  cerrarConvocatoria,
} from "@/api/endpoints/coloquios";
import type { EvaluacionCreate } from "@/api/types";
import type { ConvocatoriaFilters } from "@/features/coloquios/types";

export function useMetricas(enabled = true) {
  return useQuery({
    queryKey: ["coloquios-metricas"],
    queryFn: async () => {
      const res = await obtenerMetricas();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    enabled,
    retry: false,
  });
}

export function useConvocatoriasList(filters?: ConvocatoriaFilters) {
  return useQuery({
    queryKey: ["coloquios-convocatorias", filters],
    queryFn: async () => {
      const res = await listarConvocatorias(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useConvocatoria(evaluacionId: string) {
  return useQuery({
    queryKey: ["coloquios-convocatoria", evaluacionId],
    queryFn: async () => {
      const res = await obtenerConvocatoria(evaluacionId);
      return res.data;
    },
    enabled: !!evaluacionId,
  });
}

export function useCrearConvocatoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EvaluacionCreate) => crearConvocatoria(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-convocatorias"] });
      queryClient.invalidateQueries({ queryKey: ["coloquios-metricas"] });
    },
  });
}

export function useCerrarConvocatoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (evaluacionId: string) => cerrarConvocatoria(evaluacionId).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-convocatorias"] });
      queryClient.invalidateQueries({ queryKey: ["coloquios-metricas"] });
    },
  });
}
