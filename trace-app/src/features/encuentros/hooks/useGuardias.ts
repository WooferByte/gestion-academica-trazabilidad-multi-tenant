import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { registrarGuardia, listarGuardias, actualizarGuardia, exportarGuardiasCSV } from "@/api/endpoints/guardias";
import type { GuardiaCreate, GuardiaUpdate } from "@/api/types";

export function useGuardiasList(params?: {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
  estado?: string;
  offset?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["guardias", params],
    queryFn: async () => {
      const res = await listarGuardias(params);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useRegistrarGuardia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: GuardiaCreate) => registrarGuardia(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["guardias"] });
    },
  });
}

export function useActualizarGuardia() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: GuardiaUpdate }) =>
      actualizarGuardia(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["guardias"] });
    },
  });
}

export function useExportarGuardias() {
  return useMutation({
    mutationFn: (params?: {
      materia_id?: string;
      carrera_id?: string;
      cohorte_id?: string;
      estado?: string;
    }) => exportarGuardiasCSV(params).then((r) => r.data),
  });
}
