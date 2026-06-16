import { useQuery } from "@tanstack/react-query";
import { getMisEquipos } from "@/api/endpoints/equipos";
import type { EquipoFilters } from "@/features/equipos/types";

export function useMisEquipos(filters?: EquipoFilters) {
  return useQuery({
    queryKey: ["mis-equipos", filters],
    queryFn: async () => {
      const res = await getMisEquipos(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}
