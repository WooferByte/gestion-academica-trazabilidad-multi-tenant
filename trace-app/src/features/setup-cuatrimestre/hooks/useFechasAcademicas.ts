import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listFechas,
  createFecha,
  getFecha,
  updateFecha,
  deleteFecha,
} from "@/api/endpoints/fechas-academicas";
import type {
  FechaAcademicaCreate,
  FechaAcademicaUpdate,
} from "@/api/types";

const FECHAS_KEY = ["fechas-academicas"];

export function useFechasList(filters?: {
  materia_id?: string;
  cohorte_id?: string;
  tipo?: string;
  periodo?: string;
}) {
  return useQuery({
    queryKey: [...FECHAS_KEY, filters],
    queryFn: async () => {
      const res = await listFechas(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useFecha(fechaId: string | undefined) {
  return useQuery({
    queryKey: [...FECHAS_KEY, fechaId],
    queryFn: async () => {
      const res = await getFecha(fechaId!);
      return res.data;
    },
    enabled: !!fechaId,
  });
}

export function useCrearFecha() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FechaAcademicaCreate) =>
      createFecha(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FECHAS_KEY });
    },
  });
}

export function useActualizarFecha() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FechaAcademicaUpdate }) =>
      updateFecha(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FECHAS_KEY });
    },
  });
}

export function useEliminarFecha() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteFecha(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FECHAS_KEY });
    },
  });
}
