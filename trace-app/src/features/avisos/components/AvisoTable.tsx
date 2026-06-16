import type { AvisoResponse } from "@/api/types";

interface AvisoTableProps {
  items: AvisoResponse[];
  onEdit?: (item: AvisoResponse) => void;
  onDelete?: (item: AvisoResponse) => void;
}

const severityColors: Record<string, string> = {
  Info: "bg-blue-100 text-blue-800",
  Advertencia: "bg-yellow-100 text-yellow-800",
  Urgente: "bg-red-100 text-red-800",
};

const alcanceLabels: Record<string, string> = {
  Global: "Global",
  PorMateria: "Por Materia",
  PorCohorte: "Por Cohorte",
  PorRol: "Por Rol",
};

export function AvisoTable({ items, onEdit, onDelete }: AvisoTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-on-surface-variant">
        No se encontraron avisos
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-on-surface-variant">
            <th className="py-3 px-4 font-medium">Título</th>
            <th className="py-3 px-4 font-medium">Alcance</th>
            <th className="py-3 px-4 font-medium">Severidad</th>
            <th className="py-3 px-4 font-medium">Vigencia</th>
            <th className="py-3 px-4 font-medium">Activo</th>
            <th className="py-3 px-4 font-medium">Lecturas</th>
            {(onEdit || onDelete) && (
              <th className="py-3 px-4 font-medium">Acciones</th>
            )}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b border-border hover:bg-surface-dimmed/50">
              <td className="py-3 px-4 font-medium">{item.titulo}</td>
              <td className="py-3 px-4">
                {alcanceLabels[item.alcance] ?? item.alcance}
              </td>
              <td className="py-3 px-4">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    severityColors[item.severidad] ?? "bg-gray-100 text-gray-800"
                  }`}
                >
                  {item.severidad}
                </span>
              </td>
              <td className="py-3 px-4 text-xs">
                {new Date(item.inicio_vigencia).toLocaleDateString()} —{" "}
                {new Date(item.fin_vigencia).toLocaleDateString()}
              </td>
              <td className="py-3 px-4">
                {item.activo ? (
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Activo
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    Inactivo
                  </span>
                )}
              </td>
              <td className="py-3 px-4">{item.total_acks}</td>
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
