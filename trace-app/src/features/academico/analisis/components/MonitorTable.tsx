import { useMemo } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { exportCsv } from "@/utils/exportCsv";
import type { MonitorItem } from "@/api/types";

type MonitorTableProps = {
  items: MonitorItem[];
};

export function MonitorTable({ items }: MonitorTableProps) {
  const csvData = useMemo(
    () =>
      items.map((i) => ({
        nombre: `${i.nombre} ${i.apellido}`,
        legajo: i.legajo,
        materia: i.materia,
        comision: i.comision,
        aprobadas: `${i.actividades_aprobadas}/${i.actividades_totales}`,
        porcentaje: `${i.porcentaje}%`,
        ultima: i.ultima_actividad,
      })),
    [items],
  );

  function handleExport() {
    exportCsv(csvData, [
      { key: "nombre", label: "Nombre" },
      { key: "legajo", label: "Legajo" },
      { key: "materia", label: "Materia" },
      { key: "comision", label: "Comisión" },
      { key: "aprobadas", label: "Aprobadas" },
      { key: "porcentaje", label: "Porcentaje" },
      { key: "ultima", label: "Última actividad" },
    ], "monitor");
  }

  return (
    <div className="space-y-md">
      <div className="flex justify-end">
        <Button variant="secondary" onClick={handleExport} disabled={items.length === 0}>
          Exportar CSV
        </Button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-outline-variant bg-white">
        <table className="w-full text-left font-body-md text-body-md">
          <thead>
            <tr className="border-b border-outline-variant text-label-sm text-on-surface-variant">
              <th className="py-sm px-md">Nombre</th>
              <th className="py-sm pr-md">Legajo</th>
              <th className="py-sm pr-md">Materia</th>
              <th className="py-sm pr-md">Comisión</th>
              <th className="py-sm pr-md">Aprobadas</th>
              <th className="py-sm">Porcentaje</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-xl text-center font-body-md text-body-md text-on-surface-variant">
                  No hay datos disponibles
                </td>
              </tr>
            ) : (
              items.map((item, i) => (
                <tr
                  key={`${item.alumno_id}-${i}`}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                >
                  <td className="py-sm px-md font-medium text-on-surface">
                    {item.nombre} {item.apellido}
                  </td>
                  <td className="py-sm pr-md text-on-surface-variant">{item.legajo}</td>
                  <td className="py-sm pr-md text-on-surface">{item.materia}</td>
                  <td className="py-sm pr-md text-on-surface-variant">{item.comision}</td>
                  <td className="py-sm pr-md text-on-surface">
                    {item.actividades_aprobadas}/{item.actividades_totales}
                  </td>
                  <td className="py-sm">
                    <Badge
                      variant={
                        item.porcentaje >= 60 ? "success" : item.porcentaje >= 40 ? "warning" : "error"
                      }
                    >
                      {item.porcentaje}%
                    </Badge>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
