import { useQuery } from "@tanstack/react-query";
import { getReportesRapidos } from "@/api/endpoints/analisis";
import type { ReportesRapidosResponse } from "@/api/types";

export function useComisionKPIs(materiaId: string, cohorteId: string) {
  return useQuery<ReportesRapidosResponse>({
    queryKey: ["reportes-rapidos", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getReportesRapidos({ materia_id: materiaId, cohorte_id: cohorteId });
      return res.data;
    },
    enabled: !!(materiaId && cohorteId),
    staleTime: 2 * 60 * 1000,
  });
}
