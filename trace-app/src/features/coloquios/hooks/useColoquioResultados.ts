import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listarResultados, registrarResultado } from "@/api/endpoints/coloquios";
import type { ResultadoCreate } from "@/api/types";

export function useResultadosList(evaluacionId: string) {
  return useQuery({
    queryKey: ["coloquios-resultados", evaluacionId],
    queryFn: async () => {
      const res = await listarResultados(evaluacionId);
      return res.data;
    },
    enabled: !!evaluacionId,
  });
}

export function useRegistrarResultado() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ evaluacionId, alumnoId, data }: { evaluacionId: string; alumnoId: string; data: ResultadoCreate }) =>
      registrarResultado(evaluacionId, alumnoId, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coloquios-resultados"] });
    },
  });
}
