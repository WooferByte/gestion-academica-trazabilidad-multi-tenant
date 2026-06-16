import { Link } from "react-router-dom";
import type { EvaluacionResponse } from "@/api/types";

interface ConvocatoriaTableProps {
  items: EvaluacionResponse[];
}

const ESTADO_COLORS: Record<string, string> = {
  activa: "bg-green-100 text-green-800",
  cerrada: "bg-gray-100 text-gray-800",
};

const ESTADO_LABELS: Record<string, string> = {
  activa: "Activa",
  cerrada: "Cerrada",
};

export function ConvocatoriaTable({ items }: ConvocatoriaTableProps) {
  if (items.length === 0) {
    return (
      <p className="text-on-surface-variant text-center py-8">
        No hay convocatorias
      </p>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-variant/50">
            <th className="text-left px-4 py-3 font-medium">Instancia</th>
            <th className="text-left px-4 py-3 font-medium">Tipo</th>
            <th className="text-left px-4 py-3 font-medium">Estado</th>
            <th className="text-center px-4 py-3 font-medium">Días Disp.</th>
            <th className="text-center px-4 py-3 font-medium">Convocados</th>
            <th className="text-center px-4 py-3 font-medium">Reservas</th>
            <th className="text-center px-4 py-3 font-medium">Cupos Libres</th>
            <th className="text-right px-4 py-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {items.map((conv) => (
            <tr key={conv.id} className="hover:bg-surface-variant/30">
              <td className="px-4 py-3 font-medium">{conv.instancia}</td>
              <td className="px-4 py-3 text-on-surface-variant">{conv.tipo}</td>
              <td className="px-4 py-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${ESTADO_COLORS[conv.estado] || "bg-gray-100"}`}>
                  {ESTADO_LABELS[conv.estado] || conv.estado}
                </span>
              </td>
              <td className="px-4 py-3 text-center">{conv.dias_disponibles}</td>
              <td className="px-4 py-3 text-center">{conv.total_convocados}</td>
              <td className="px-4 py-3 text-center">{conv.reservas_activas}</td>
              <td className="px-4 py-3 text-center">{conv.cupos_libres}</td>
              <td className="px-4 py-3 text-right">
                <Link
                  to={`/coloquios/${conv.id}`}
                  className="text-xs px-3 py-1 rounded border border-border hover:bg-surface-variant transition-colors"
                >
                  Ver detalle
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
