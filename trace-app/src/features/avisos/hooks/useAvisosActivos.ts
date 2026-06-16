import { useQuery } from "@tanstack/react-query";
import { listarAvisos } from "@/api/endpoints/avisos";

export function useAvisosActivos(refetchInterval?: number) {
  return useQuery({
    queryKey: ["avisos-activos"],
    queryFn: async () => {
      const res = await listarAvisos();
      const now = new Date();
      const activos = res.data.items.filter(
        (a) =>
          a.activo &&
          new Date(a.inicio_vigencia) <= now &&
          new Date(a.fin_vigencia) >= now,
      );
      return { items: activos, total: activos.length };
    },
    refetchInterval: refetchInterval ?? false,
    staleTime: 60 * 1000,
  });
}
