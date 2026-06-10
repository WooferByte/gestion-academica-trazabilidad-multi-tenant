import { useQuery } from "@tanstack/react-query";
import { getRanking } from "@/api/endpoints/analisis";
import type { RankingResponse } from "@/api/types";

export function useRanking(materiaId: string, cohorteId: string) {
  return useQuery<RankingResponse>({
    queryKey: ["ranking", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getRanking({ materia_id: materiaId, cohorte_id: cohorteId });
      return res.data;
    },
    enabled: !!(materiaId && cohorteId),
  });
}
