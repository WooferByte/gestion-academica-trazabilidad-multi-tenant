import { useMemo } from "react";
import { useParams, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import type { Comision } from "@/api/types";

const SUBPAGE_LABELS: Record<string, string> = {
  importar: "Importar",
  umbral: "Umbral",
  atrasados: "Atrasados",
  ranking: "Ranking",
  notas: "Notas Finales",
  "tps-sin-corregir": "TPs sin corregir",
  comunicar: "Comunicar",
  monitor: "Monitor",
};

interface BreadcrumbItem {
  label: string;
  path: string;
}

export function useBreadcrumb(): BreadcrumbItem[] {
  const { materiaId, cohorteId } = useParams<{
    materiaId: string;
    cohorteId: string;
  }>();
  const location = useLocation();

  const { data: comisiones } = useQuery<Comision[]>({
    queryKey: ["docente", "comisiones"],
    queryFn: async () => {
      const res = await api.get<Comision[]>("/docente/comisiones");
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!(materiaId && cohorteId),
  });

  return useMemo(() => {
    const items: BreadcrumbItem[] = [
      { label: "Académico", path: "/academico" },
    ];

    if (materiaId && cohorteId && comisiones) {
      const com = comisiones.find(
        (c) => c.materia_id === materiaId && c.cohorte_id === cohorteId,
      );
      if (com) {
        items.push({
          label: com.materia_nombre,
          path: `/academico/${materiaId}/${cohorteId}`,
        });
        items.push({
          label: com.cohorte_nombre,
          path: `/academico/${materiaId}/${cohorteId}`,
        });
      }
    }

    const segments = location.pathname.split("/").filter(Boolean);
    for (const seg of segments) {
      if (seg === "academico" || seg === materiaId || seg === cohorteId) continue;
      const label = SUBPAGE_LABELS[seg] ?? seg;
      items.push({ label, path: "" });
    }

    return items;
  }, [materiaId, cohorteId, location.pathname, comisiones]);
}
