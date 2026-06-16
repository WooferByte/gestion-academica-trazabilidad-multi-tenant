const estadoColors: Record<string, string> = {
  Pendiente: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  "En progreso": "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  Resuelta: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  Cancelada: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
};

const estadoLabels: Record<string, string> = {
  Pendiente: "Pendiente",
  "En progreso": "En Progreso",
  Resuelta: "Resuelta",
  Cancelada: "Cancelada",
};

interface TareaEstadoBadgeProps {
  estado: string;
}

export function TareaEstadoBadge({ estado }: TareaEstadoBadgeProps) {
  const colorClass = estadoColors[estado] ?? "bg-gray-100 text-gray-800";
  const label = estadoLabels[estado] ?? estado;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}
    >
      {label}
    </span>
  );
}
