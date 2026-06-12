import { useMemo } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useTpsSinCorregir } from "@/features/academico/analisis/hooks/useTpsSinCorregir";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { exportCsv } from "@/utils/exportCsv";

export default function TpsSinCorregirPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { data, isLoading } = useTpsSinCorregir(materiaId!, cohorteId!);
  const tps = data?.items ?? [];

  const csvData = useMemo(
    () =>
      tps.map((t) => ({
        nombre: `${t.nombre} ${t.apellido}`,
        comision: t.comision,
        actividad: t.actividad,
      })),
    [tps],
  );

  function handleExport() {
    exportCsv(csvData, [
      { key: "nombre", label: "Nombre" },
      { key: "comision", label: "Comisión" },
      { key: "actividad", label: "Actividad" },
    ], "tps-sin-corregir");
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
        <h1 className="font-headline-md text-headline-md text-on-surface">TPs sin corregir</h1>
        <Button variant="secondary" onClick={handleExport} disabled={tps.length === 0}>
          Exportar CSV
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-sm">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant bg-white">
          <table className="w-full text-left font-body-md text-body-md">
            <thead>
              <tr className="border-b border-outline-variant text-label-sm text-on-surface-variant">
                <th className="py-sm px-md">Nombre</th>
                <th className="py-sm pr-md">Comisión</th>
                <th className="py-sm pr-md">Actividad</th>
              </tr>
            </thead>
            <tbody>
              {tps.length === 0 ? (
                <tr>
                  <td colSpan={3} className="py-xl text-center font-body-md text-body-md text-on-surface-variant">
                    No hay TPs sin corregir
                  </td>
                </tr>
              ) : (
                tps.map((tp, idx) => (
                  <tr
                    key={`${tp.entrada_padron_id}-${tp.actividad}`}
                    className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                  >
                    <td className="py-sm px-md font-medium text-on-surface">
                      {tp.nombre} {tp.apellido}
                    </td>
                    <td className="py-sm pr-md text-on-surface-variant">{tp.comision}</td>
                    <td className="py-sm pr-md text-on-surface">{tp.actividad}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
