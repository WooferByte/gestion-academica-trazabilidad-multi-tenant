import { useQuery } from "@tanstack/react-query";
import { getComunicacionesTracking } from "@/api/endpoints/comunicaciones";
import type { ComunicacionesTrackingResponse } from "@/api/types";

export function useComunicacionesTracking(loteId: string) {
  return useQuery<ComunicacionesTrackingResponse>({
    queryKey: ["comunicaciones-tracking", loteId],
    queryFn: async () => {
      const res = await getComunicacionesTracking({ lote_id: loteId });
      return res.data;
    },
    enabled: !!loteId,
    refetchInterval: (query) => {
      const data = query.state.data;
      const hasInFlight = data?.items.some(
        (i) => i.estado === "enviando" || i.estado === "pendiente",
      );
      return hasInFlight ? 5000 : false;
    },
  });
}
