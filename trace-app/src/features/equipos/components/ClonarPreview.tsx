import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { AsignacionResponse } from "@/api/types";

interface SelectItem {
  id: string;
  nombre: string;
}

function useNameMap(queryKey: string[], url: string): Record<string, string> {
  const { data } = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const res = await api.get(url);
        return (res.data?.items ?? []) as SelectItem[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });
  return useMemo(() => {
    const map: Record<string, string> = {};
    for (const item of data ?? []) map[item.id] = item.nombre;
    return map;
  }, [data]);
}

function resolve(obj: Record<string, string>, key: string, map: Record<string, string>): string {
  if (!key) return "—";
  return map[key] ?? key;
}

interface ClonarPreviewProps {
  origen: { materia_id: string; carrera_id: string; cohorte_id: string } | null;
  destino: { materia_id: string; carrera_id: string; cohorte_id: string } | null;
  previewItems?: AsignacionResponse[];
  isLoading?: boolean;
}

export function ClonarPreview({
  origen,
  destino,
  previewItems,
  isLoading,
}: ClonarPreviewProps) {
  const materias = useNameMap(["materias", "preview"], "/admin/materias");
  const carreras = useNameMap(["carreras", "preview"], "/admin/carreras");
  const cohortes = useNameMap(["cohortes", "preview"], "/admin/cohortes");

  if (!origen || !destino) {
    return (
      <div className="text-center py-8 text-on-surface-variant">
        Seleccioná origen y destino para ver la previsualización
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded-lg border border-border bg-surface-dimmed/30">
          <h3 className="text-sm font-medium mb-2">Origen</h3>
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Materia:</dt>
              <dd>{resolve(origen, origen.materia_id, materias)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Carrera:</dt>
              <dd>{resolve(origen, origen.carrera_id, carreras)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Cohorte:</dt>
              <dd>{resolve(origen, origen.cohorte_id, cohortes)}</dd>
            </div>
          </dl>
        </div>
        <div className="p-4 rounded-lg border border-border bg-surface-dimmed/30">
          <h3 className="text-sm font-medium mb-2">Destino</h3>
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Materia:</dt>
              <dd>{resolve(destino, destino.materia_id, materias)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Carrera:</dt>
              <dd>{resolve(destino, destino.carrera_id, carreras)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-on-surface-variant">Cohorte:</dt>
              <dd>{resolve(destino, destino.cohorte_id, cohortes)}</dd>
            </div>
          </dl>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-4 text-on-surface-variant">
          Calculando preview...
        </div>
      )}

      {previewItems && (
        <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
          <p className="text-sm font-medium">
            Se clonarán <strong>{previewItems.length}</strong> asignaciones
          </p>
        </div>
      )}
    </div>
  );
}
