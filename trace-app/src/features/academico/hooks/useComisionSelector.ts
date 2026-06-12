import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { useAuth } from "@/features/auth/hooks/useAuth";
import type { Comision } from "@/api/types";

export function useComisionSelector() {
  const { user } = useAuth();
  const query = useQuery<Comision[]>({
    queryKey: ["docente", "comisiones", user?.id],
    queryFn: async () => {
      const res = await api.get<Comision[]>("/docente/comisiones");
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Deduplicate materias by ID (not by name, in case two materias share a name)
  const materiasUnicas = query.data
    ? Array.from(new Map(query.data.map((c) => [c.materia_id, { materia_id: c.materia_id, materia_nombre: c.materia_nombre }])).values())
    : [];

  function getCohortes(materiaId: string) {
    return query.data
      ?.filter((com) => com.materia_id === materiaId)
      .map((com) => ({ cohorte_id: com.cohorte_id, cohorte_nombre: com.cohorte_nombre })) ?? [];
  }

  return { query, comisiones: query.data ?? [], materiasUnicas, getCohortes };
}
