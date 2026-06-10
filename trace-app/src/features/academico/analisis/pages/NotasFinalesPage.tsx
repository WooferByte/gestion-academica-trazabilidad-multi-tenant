import { useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useNotasFinales } from "@/features/academico/analisis/hooks/useNotasFinales";
import { getActividades } from "@/api/endpoints/analisis";
import { ActivitySelector } from "@/features/academico/analisis/components/ActivitySelector";
import { GradeMatrix } from "@/features/academico/analisis/components/GradeMatrix";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

export default function NotasFinalesPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [viewActividades, setViewActividades] = useState<string[]>([]);

  const { data: actividadesData, isLoading: loadingActividades } = useQuery({
    queryKey: ["actividades", materiaId, cohorteId],
    queryFn: async () => {
      const res = await getActividades({ materia_id: materiaId!, cohorte_id: cohorteId! });
      return res.data.items.map((a) => ({ id: a.id, nombre: a.nombre }));
    },
    enabled: !!(materiaId && cohorteId),
  });

  const { data: notasData, isFetching } = useNotasFinales(materiaId!, cohorteId!, viewActividades);

  const actividades = useMemo(() => actividadesData ?? [], [actividadesData]);
  const alumnos = useMemo(() => notasData?.items ?? [], [notasData?.items]);

  return (
    <div className="space-y-lg p-lg">
      <nav className="flex items-center gap-xs font-body-sm text-body-sm text-on-surface-variant">
        {breadcrumb.map((b, i) => (
          <span key={i} className="flex items-center gap-xs">
            {i > 0 && <span className="material-symbols-outlined text-[16px]">chevron_right</span>}
            {b.path ? (
              <a href={b.path} className="hover:text-primary transition-colors">{b.label}</a>
            ) : (
              <span className="text-on-surface">{b.label}</span>
            )}
          </span>
        ))}
      </nav>

      <h1 className="font-headline-md text-headline-md text-on-surface">Notas Finales</h1>

      {viewActividades.length === 0 ? (
        <div className="rounded-xl border border-outline-variant bg-white p-lg">
          <ActivitySelector
            actividades={actividades}
            selectedIds={selectedIds}
            onToggle={(id) =>
              setSelectedIds((prev) =>
                prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
              )
            }
            onView={() => setViewActividades(selectedIds)}
          />
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
            <p className="font-body-md text-body-md text-on-surface-variant">
              {viewActividades.length} actividad{viewActividades.length !== 1 ? "es" : ""} seleccionada{viewActividades.length !== 1 ? "s" : ""}
            </p>
            <Button variant="secondary" onClick={() => setViewActividades([])}>
              Cambiar actividades
            </Button>
          </div>

          {isFetching ? (
            <div className="space-y-sm">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <GradeMatrix actividades={viewActividades.map((n) => ({ id: n, nombre: n }))} alumnos={alumnos} />
          )}
        </>
      )}
    </div>
  );
}
