import { useQuery } from "@tanstack/react-query";
import { listarAvisos } from "@/api/endpoints/avisos";
import type { AvisoFilters } from "@/features/avisos/types";

export function useAvisos(filters?: AvisoFilters) {
  return useQuery({
    queryKey: ["avisos", filters],
    queryFn: async () => {
      const res = await listarAvisos();
      let items = res.data.items;

      if (filters) {
        if (filters.activo !== undefined) {
          items = items.filter((a) => a.activo === filters.activo);
        }
        if (filters.alcance) {
          items = items.filter((a) => a.alcance === filters.alcance);
        }
      }

      return { items, total: items.length };
    },
    staleTime: 2 * 60 * 1000,
  });
}
