import { useNavigate } from "react-router-dom";
import { TareaEstadoBadge } from "./TareaEstadoBadge";
import type { TareaResponse } from "@/api/types";

interface TareasAdminTableProps {
  items: TareaResponse[];
}

export function TareasAdminTable({ items }: TareasAdminTableProps) {
  const navigate = useNavigate();

  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No se encontraron tareas
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Descripción</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Estado</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Asignado a</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Asignado por</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Creada</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((tarea) => (
            <tr
              key={tarea.id}
              className="border-b border-border hover:bg-accent/50 cursor-pointer"
              onClick={() => navigate(`/tareas/${tarea.id}`)}
            >
              <td className="py-3 px-4 max-w-xs truncate">{tarea.descripcion}</td>
              <td className="py-3 px-4">
                <TareaEstadoBadge estado={tarea.estado} />
              </td>
              <td className="py-3 px-4">{tarea.asignado_a_nombre ?? tarea.asignado_a.slice(0, 8)}</td>
              <td className="py-3 px-4">{tarea.asignado_por_nombre ?? tarea.asignado_por.slice(0, 8)}</td>
              <td className="py-3 px-4">
                {tarea.created_at ? new Date(tarea.created_at).toLocaleDateString("es-AR") : "-"}
              </td>
              <td className="py-3 px-4">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/tareas/${tarea.id}`);
                  }}
                  className="text-sm text-primary hover:underline"
                >
                  Ver
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
