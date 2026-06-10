import { useQuery } from "@tanstack/react-query";
import { getMonitorSeguimiento, getMonitorGeneral } from "@/api/endpoints/analisis";
import { useAuth } from "@/features/auth/hooks/useAuth";

interface MonitorFilters {
  materia_id?: string;
  comision_id?: string;
  q?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}

export function useMonitor(filters: MonitorFilters) {
  const { permissions } = useAuth();
  const isCoordinador = permissions.includes("comunicacion:aprobar");

  return useQuery({
    queryKey: ["monitor", isCoordinador ? "general" : "seguimiento", filters],
    queryFn: async () => {
      if (isCoordinador) {
        const res = await getMonitorGeneral(filters);
        return res.data;
      }
      const res = await getMonitorSeguimiento(filters);
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}
