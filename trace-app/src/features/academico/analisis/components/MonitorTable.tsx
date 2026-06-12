import { useMemo } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { exportCsv } from "@/utils/exportCsv";
import type { MonitorGeneralItem, MonitorSeguimientoItem } from "@/api/types";

type MonitorTableProps = {
  items: (MonitorGeneralItem | MonitorSeguimientoItem)[];
  isGeneral: boolean;
};

export function MonitorTable({ items, isGeneral }: MonitorTableProps) {
  const csvData = useMemo(
    () =>
      items.map((i) => ({
        nombre: `${i.nombre} ${i.apellidos}`,
        comision: i.comision,
        materia: isGeneral ? (i as MonitorGeneralItem).materia_nombre : "—",
        actividad: i.actividad,
        nota: i.nota_numerica ?? i.nota_textual ?? "—",
        aprobado: i.aprobado !== null ? (i.aprobado ? "Sí" : "No") : "—",
        regional: isGeneral ? (i as MonitorGeneralItem).regional : "—",
      })),
    [items, isGeneral],
  );

  function handleExport() {
    exportCsv(csvData, [
      { key: "nombre", label: "Nombre" },
      { key: "comision", label: "Comisión" },
      { key: "materia", label: "Materia" },
      { key: "actividad", label: "Actividad" },
      { key: "nota", label: "Nota" },
      { key: "aprobado", label: "Aprobado" },
      { key: "regional", label: "Regional" },
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
              <th className="py-sm pr-md">Comisión</th>
              {isGeneral && <th className="py-sm pr-md">Regional</th>}
              {isGeneral && <th className="py-sm pr-md">Materia</th>}
              <th className="py-sm pr-md">Actividad</th>
              <th className="py-sm pr-md">Nota</th>
              <th className="py-sm">Aprobado</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={isGeneral ? 7 : 5} className="py-xl text-center font-body-md text-body-md text-on-surface-variant">
                  No hay datos disponibles
                </td>
              </tr>
            ) : (
              items.map((item, i) => {
                const general = isGeneral ? (item as MonitorGeneralItem) : null;
                return (
                  <tr
                    key={`${item.entrada_padron_id}-${item.actividad}-${i}`}
                    className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
                  >
                    <td className="py-sm px-md font-medium text-on-surface">
                      {item.nombre} {item.apellidos}
                    </td>
                    <td className="py-sm pr-md text-on-surface-variant">{item.comision}</td>
                    {isGeneral && <td className="py-sm pr-md text-on-surface-variant">{general!.regional}</td>}
                    {isGeneral && <td className="py-sm pr-md text-on-surface">{general!.materia_nombre}</td>}
                    <td className="py-sm pr-md text-on-surface">{item.actividad}</td>
                    <td className="py-sm pr-md text-on-surface">
                      {item.nota_numerica ?? item.nota_textual ?? "—"}
                    </td>
                    <td className="py-sm">
                      {item.aprobado === null ? (
                        <span className="text-on-surface-variant">—</span>
                      ) : (
                        <Badge variant={item.aprobado ? "success" : "error"}>
                          {item.aprobado ? "Aprobado" : "Desaprobado"}
                        </Badge>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
