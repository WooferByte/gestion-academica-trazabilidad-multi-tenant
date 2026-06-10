import { Badge } from "@/components/ui/Badge";
import type { AlumnoAtrasado } from "@/api/types";

type AtrasadosTableProps = {
  alumnos: AlumnoAtrasado[];
  selectedIds: string[];
  onToggle: (id: string) => void;
};

export function AtrasadosTable({ alumnos, selectedIds, onToggle }: AtrasadosTableProps) {
  if (alumnos.length === 0) {
    return (
      <div className="flex flex-col items-center gap-md py-xl text-center">
        <span className="material-symbols-outlined text-4xl text-green-600">check_circle</span>
        <p className="font-body-lg text-body-lg text-on-surface">No hay alumnos atrasados</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left font-body-md text-body-md">
        <thead>
          <tr className="border-b border-outline-variant text-label-sm text-on-surface-variant">
            <th className="w-10 py-sm pr-xs">
              <input
                type="checkbox"
                checked={selectedIds.length === alumnos.length}
                onChange={() => {
                  if (selectedIds.length === alumnos.length) {
                    selectedIds.forEach((id) => onToggle(id));
                  } else {
                    alumnos.forEach((a) => {
                      if (!selectedIds.includes(a.entrada_padron_id)) onToggle(a.entrada_padron_id);
                    });
                  }
                }}
                className="h-4 w-4 accent-primary"
              />
            </th>
            <th className="py-sm pr-md">Nombre</th>
            <th className="py-sm pr-md">Comisión</th>
            <th className="py-sm pr-md">Regional</th>
            <th className="py-sm pr-md">Actividades</th>
            <th className="py-sm pr-md">Faltantes</th>
            <th className="py-sm">Desaprobadas</th>
          </tr>
        </thead>
        <tbody>
          {alumnos.map((alumno) => (
            <tr
              key={alumno.entrada_padron_id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container last:border-0"
            >
              <td className="py-sm pr-xs">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(alumno.entrada_padron_id)}
                  onChange={() => onToggle(alumno.entrada_padron_id)}
                  className="h-4 w-4 accent-primary"
                />
              </td>
              <td className="py-sm pr-md font-medium text-on-surface">
                {alumno.nombre} {alumno.apellidos}
              </td>
              <td className="py-sm pr-md text-on-surface-variant">{alumno.comision}</td>
              <td className="py-sm pr-md text-on-surface-variant">{alumno.regional}</td>
              <td className="py-sm pr-md text-on-surface-variant">
                {alumno.aprobadas}/{alumno.total_actividades}
              </td>
              <td className="py-sm pr-md">
                <div className="flex flex-wrap gap-1">
                  {alumno.actividades_faltantes.map((act) => (
                    <Badge key={act} variant="warning">{act}</Badge>
                  ))}
                </div>
              </td>
              <td className="py-sm">
                <div className="flex flex-wrap gap-1">
                  {alumno.actividades_desaprobadas.map((act) => (
                    <Badge key={act} variant="error">{act}</Badge>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
