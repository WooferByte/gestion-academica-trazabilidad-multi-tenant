import { useQuery } from "@tanstack/react-query";
import { getNotasFinales } from "@/api/endpoints/analisis";
import type { NotasFinalesResponse } from "@/api/types";

export function useNotasFinales(
  materiaId: string,
  cohorteId: string,
  actividades: string[],
) {
  return useQuery<NotasFinalesResponse>({
    queryKey: ["notas-finales", materiaId, cohorteId, actividades],
    queryFn: async () => {
      const res = await getNotasFinales({
        materia_id: materiaId,
        cohorte_id: cohorteId,
        actividades: actividades.join(","),
      });
      return res.data;
    },
    enabled: !!(materiaId && cohorteId && actividades.length > 0),
  });
}
