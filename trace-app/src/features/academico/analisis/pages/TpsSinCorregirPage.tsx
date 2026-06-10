import { useMemo } from "react";
import { useParams } from "react-router-dom";
import { useBreadcrumb } from "@/features/academico/hooks/useBreadcrumb";
import { useTpsSinCorregir } from "@/features/academico/analisis/hooks/useTpsSinCorregir";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { exportCsv } from "@/utils/exportCsv";

export default function TpsSinCorregirPage() {
  const { materiaId, cohorteId } = useParams<{ materiaId: string; cohorteId: string }>();
  const breadcrumb = useBreadcrumb();
  const { data, isLoading } = useTpsSinCorregir(materiaId!, cohorteId!);
  const tps = data?.tps ?? [];

  const csvData = useMemo(
    () =>
      tps.map((t) => ({
        nombre: `${t.nombre} ${t.apellido}`,
        legajo: t.legajo,
        actividad: t.actividad_nombre,
        tipo: t.actividad_tipo,
        fecha: t.fecha_entrega,
      })),
    [tps],
  );

  function handleExport() {
    exportCsv(csvData, [
      { key: "nombre", label: "Nombre" },
      { key: "legajo", label: "Legajo" },
      { key: "actividad", label: "Actividad" },
      { key: "tipo", label: "Tipo" },
      { key: "fecha", label: "Fecha de entrega" },
    ], "tps-sin-corregir");
  }

  return (
    <div className="space-y-lg">
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
                <th className="py-sm pr-md">Legajo</th>
                <th className="py-sm pr-md">Actividad</th>
                <th className="py-sm pr-md">Tipo</th>
                <th className="py-sm">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {tps.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-xl text-center font-body-md text-body-md text-on-surface-variant">
                    No hay TPs sin corregir
                  </td>
                </tr>
              ) : (
                tps.map((tp) => (
                  <tr
                    key={tp.id}
                    className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                  >
                    <td className="py-sm px-md font-medium text-on-surface">
                      {tp.nombre} {tp.apellido}
                    </td>
                    <td className="py-sm pr-md text-on-surface-variant">{tp.legajo}</td>
                    <td className="py-sm pr-md text-on-surface">{tp.actividad_nombre}</td>
                    <td className="py-sm pr-md">
                      <Badge variant="info">{tp.actividad_tipo}</Badge>
                    </td>
                    <td className="py-sm text-on-surface-variant">{tp.fecha_entrega}</td>
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
