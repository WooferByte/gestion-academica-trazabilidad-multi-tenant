import type { NotaFinalAlumno } from "@/api/types";

type GradeMatrixProps = {
  actividades: Array<{ id: string; nombre: string }>;
  alumnos: NotaFinalAlumno[];
};

export function GradeMatrix({ actividades, alumnos }: GradeMatrixProps) {
  if (alumnos.length === 0) {
    return (
      <div className="flex flex-col items-center gap-md py-xl text-center">
        <span className="font-body-md text-body-md text-on-surface-variant">
          No hay datos para las actividades seleccionadas
        </span>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant bg-white">
      <table className="w-full text-left font-body-sm text-body-sm">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container">
            <th className="py-sm px-md font-label-sm text-on-surface-variant">#</th>
            <th className="py-sm pr-md font-label-sm text-on-surface-variant">Nombre</th>
            <th className="py-sm pr-md font-label-sm text-on-surface-variant">Actividades</th>
            <th className="py-sm pr-md font-label-sm text-on-surface-variant">Nota Final</th>
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
              <td className="py-sm pr-md text-on-surface-variant">
                {actividades.length}
              </td>
              <td className="py-sm pr-md text-on-surface">
                {alumno.nota_final != null ? alumno.nota_final.toFixed(2) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
