import type { ProgramaMateriaResponse } from "@/api/types";

interface ProgramaTableProps {
  items: ProgramaMateriaResponse[];
  onEdit: (item: ProgramaMateriaResponse) => void;
  onDelete: (item: ProgramaMateriaResponse) => void;
}

export function ProgramaTable({ items, onEdit, onDelete }: ProgramaTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No hay programas cargados para esta selección
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Materia</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Título</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Archivo</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Cargado</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((programa) => (
            <tr key={programa.id} className="border-b border-border hover:bg-accent/50">
              <td className="py-3 px-4">{programa.materia_id.slice(0, 8)}</td>
              <td className="py-3 px-4 font-medium">{programa.titulo}</td>
              <td className="py-3 px-4">
                {programa.referencia_archivo ? (
                  <span className="text-primary text-xs">{programa.referencia_archivo}</span>
                ) : (
                  <span className="text-muted-foreground">-</span>
                )}
              </td>
              <td className="py-3 px-4 text-muted-foreground">
                {programa.cargado_at
                  ? new Date(programa.cargado_at).toLocaleDateString("es-AR")
                  : "-"}
              </td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(programa)}
                    className="text-sm text-primary hover:underline"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(programa)}
                    className="text-sm text-destructive hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
