import type { AsignacionResponse } from "@/api/types";

interface AsignacionTableProps {
  items: AsignacionResponse[];
  onEdit?: (item: AsignacionResponse) => void;
  onDelete?: (item: AsignacionResponse) => void;
}

export function AsignacionTable({ items, onEdit, onDelete }: AsignacionTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-on-surface-variant">
        No se encontraron asignaciones
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-on-surface-variant">
            <th className="py-3 px-4 font-medium">Docente</th>
            <th className="py-3 px-4 font-medium">Rol</th>
            <th className="py-3 px-4 font-medium">Materia</th>
            <th className="py-3 px-4 font-medium">Carrera</th>
            <th className="py-3 px-4 font-medium">Cohorte</th>
            <th className="py-3 px-4 font-medium">Comisiones</th>
            <th className="py-3 px-4 font-medium">Vigencia</th>
            {(onEdit || onDelete) && (
              <th className="py-3 px-4 font-medium">Acciones</th>
            )}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-border hover:bg-surface-dimmed/50">
              <td className="py-3 px-4">{item.usuario_nombre || item.usuario_id}</td>
              <td className="py-3 px-4">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                  {item.rol}
                </span>
              </td>
              <td className="py-3 px-4">{item.materia_nombre ?? "—"}</td>
              <td className="py-3 px-4">{item.carrera_nombre ?? "—"}</td>
              <td className="py-3 px-4">{item.cohorte_nombre ?? "—"}</td>
              <td className="py-3 px-4">{item.comisiones?.join(", ") ?? "—"}</td>
              <td className="py-3 px-4 text-xs">
                {item.desde ? (
                  <span>
                    {new Date(item.desde).toLocaleDateString()} — {item.hasta ? new Date(item.hasta).toLocaleDateString() : "∞"}
                  </span>
                ) : (
                  "—"
                )}
              </td>
              {(onEdit || onDelete) && (
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(item)}
                        className="text-primary hover:text-primary/80 text-sm"
                        aria-label="Editar"
                      >
                        Editar
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={() => onDelete(item)}
                        className="text-destructive hover:text-destructive/80 text-sm"
                        aria-label="Eliminar"
                      >
                        Eliminar
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
