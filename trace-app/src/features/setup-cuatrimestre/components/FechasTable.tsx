import type { FechaAcademicaResponse } from "@/api/types";

interface FechasTableProps {
  items: FechaAcademicaResponse[];
  onEdit: (item: FechaAcademicaResponse) => void;
  onDelete: (item: FechaAcademicaResponse) => void;
}

export function FechasTable({ items, onEdit, onDelete }: FechasTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No hay fechas académicas registradas
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Fecha</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Título</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Tipo</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Nº</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Período</th>
            <th className="text-left py-3 px-4 font-medium text-muted-foreground">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((fecha) => (
            <tr key={fecha.id} className="border-b border-border hover:bg-accent/50">
              <td className="py-3 px-4 font-medium">
                {new Date(fecha.fecha).toLocaleDateString("es-AR")}
              </td>
              <td className="py-3 px-4">{fecha.titulo}</td>
              <td className="py-3 px-4">
                <span className="capitalize">{fecha.tipo}</span>
              </td>
              <td className="py-3 px-4">{fecha.numero}</td>
              <td className="py-3 px-4">{fecha.periodo}</td>
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(fecha)}
                    className="text-sm text-primary hover:underline"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(fecha)}
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
