import { useMutation, useQueryClient } from "@tanstack/react-query";
import { vaciarMateria } from "@/api/endpoints/padron";

export function useVaciarMateria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ materiaId, cohorteId }: { materiaId: string; cohorteId: string }) =>
      vaciarMateria(materiaId, cohorteId).then((r) => r.data),
    onSuccess: (_data, variables) => {
      // Invalidate all analysis queries so KPIs, atrasados, TPs refresh automatically
      queryClient.invalidateQueries({ queryKey: ["reportes-rapidos", variables.materiaId, variables.cohorteId] });
      queryClient.invalidateQueries({ queryKey: ["atrasados", variables.materiaId, variables.cohorteId] });
      queryClient.invalidateQueries({ queryKey: ["tps-sin-corregir", variables.materiaId, variables.cohorteId] });
    },
  });
}
