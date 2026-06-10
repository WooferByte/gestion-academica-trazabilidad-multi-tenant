import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useRanking } from "@/features/academico/analisis/hooks/useRanking";
import { Skeleton } from "@/components/ui/Skeleton";

export default function RankingPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { data, isLoading } = useRanking(materiaId!, cohorteId!);
  const alumnos = data?.items ?? [];

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

      <h1 className="font-headline-md text-headline-md text-on-surface">Ranking</h1>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant bg-white">
          <table className="w-full text-left font-body-md text-body-md">
            <thead>
              <tr className="border-b border-outline-variant text-label-sm text-on-surface-variant">
                <th className="w-12 py-sm px-md">#</th>
                <th className="py-sm pr-md">Nombre</th>
                <th className="py-sm pr-md">Comisión</th>
                <th className="py-sm">Aprobadas</th>
              </tr>
            </thead>
            <tbody>
              {alumnos.map((alumno, i) => (
                <tr
                  key={alumno.entrada_padron_id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                >
                  <td className="py-sm px-md font-label-lg text-label-lg text-secondary">{i + 1}</td>
                  <td className="py-sm pr-md font-medium text-on-surface">
                    {alumno.nombre} {alumno.apellidos}
                  </td>
                  <td className="py-sm pr-md text-on-surface-variant">{alumno.comision}</td>
                  <td className="py-sm font-medium text-on-surface">{alumno.actividades_aprobadas}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
