import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getUmbral, updateUmbral } from "@/api/endpoints/umbrales";
import type { UmbralResponse } from "@/api/types";

export function useUmbral(materiaId: string, cohorteId: string) {
  return useQuery<UmbralResponse>({
    queryKey: ["umbral", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getUmbral(materiaId, cohorteId);
      return res.data;
    },
    enabled: !!(materiaId && cohorteId),
  });
}

export function useUmbralMutation(materiaId: string, cohorteId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (umbral_pct: number) => updateUmbral(materiaId, cohorteId, { umbral_pct }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["umbral", materiaId, cohorteId] });
      queryClient.invalidateQueries({ queryKey: ["reportes-rapidos", materiaId, cohorteId] });
      queryClient.invalidateQueries({ queryKey: ["atrasados", materiaId, cohorteId] });
      queryClient.invalidateQueries({ queryKey: ["ranking", materiaId, cohorteId] });
    },
  });
}
