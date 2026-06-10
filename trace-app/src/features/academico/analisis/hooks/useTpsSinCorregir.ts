import { useQuery } from "@tanstack/react-query";
import { getTpsSinCorregir } from "@/api/endpoints/analisis";
import type { TpsSinCorregirResponse } from "@/api/types";

export function useTpsSinCorregir(materiaId: string, cohorteId: string) {
  return useQuery<TpsSinCorregirResponse>({
    queryKey: ["tps-sin-corregir", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getTpsSinCorregir({ materia_id: materiaId, cohorte_id: cohorteId });
      return res.data;
    },
    enabled: !!(materiaId && cohorteId),
  });
}
