import { useQuery } from "@tanstack/react-query";
import { getMonitorSeguimiento, getMonitorGeneral } from "@/api/endpoints/analisis";
import { useAuth } from "@/features/auth/hooks/useAuth";

interface MonitorFilters {
  materia_id?: string;
  q?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

export function useMonitor(filters: MonitorFilters) {
  const { permissions, user } = useAuth();
  const isCoordinador = permissions.includes("comunicacion:aprobar");

  // Map frontend filter names -> backend param names
  const backendParams = {
    ...(filters.materia_id && { materia_id: filters.materia_id }),
    ...(filters.q && { busqueda: filters.q }),
    ...(!isCoordinador && filters.fecha_desde && { desde: filters.fecha_desde }),
    ...(!isCoordinador && filters.fecha_hasta && { hasta: filters.fecha_hasta }),
  };

  return useQuery({
    queryKey: ["monitor", isCoordinador ? "general" : "seguimiento", user?.id, filters],
    queryFn: async () => {
      if (isCoordinador) {
        const res = await getMonitorGeneral(backendParams);
        return res.data;
      }
      const res = await getMonitorSeguimiento(backendParams);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}
