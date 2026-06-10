import { useQuery } from "@tanstack/react-query";
import { getAtrasados } from "@/api/endpoints/analisis";
import type { AtrasadosResponse } from "@/api/types";

export function useAtrasados(materiaId: string, cohorteId: string) {
  return useQuery<AtrasadosResponse>({
    queryKey: ["atrasados", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getAtrasados({ materia_id: materiaId, cohorte_id: cohorteId });
      return res.data;
    },
    enabled: !!(materiaId && cohorteId),
  });
}
