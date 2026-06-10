import { useState } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useAtrasados } from "@/features/academico/analisis/hooks/useAtrasados";
import { AtrasadosTable } from "@/features/academico/analisis/components/AtrasadosTable";
import { ComunicarButton } from "@/features/academico/analisis/components/ComunicarButton";
import { Skeleton } from "@/components/ui/Skeleton";

export default function AtrasadosPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { data, isLoading } = useAtrasados(materiaId!, cohorteId!);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  function handleToggle(id: string) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

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

      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">Alumnos atrasados</h1>
        <ComunicarButton selectedIds={selectedIds} />
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <AtrasadosTable
          alumnos={data?.items ?? []}
          selectedIds={selectedIds}
          onToggle={handleToggle}
        />
      )}
    </div>
  );
}
