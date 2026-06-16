import type { FechaAcademicaResponse } from "@/api/types";

interface FechaCardProps {
  fecha: FechaAcademicaResponse;
  onClick?: () => void;
}

const tipoColors: Record<string, string> = {
  parcial: "border-l-blue-500",
  tp: "border-l-green-500",
  coloquio: "border-l-purple-500",
  recuperatorio: "border-l-amber-500",
  final: "border-l-red-500",
};

export function FechaCard({ fecha, onClick }: FechaCardProps) {
  const colorClass = tipoColors[fecha.tipo] ?? "border-l-gray-500";

  return (
    <div
      onClick={onClick}
      className={`rounded-md border border-border bg-surface p-3 border-l-4 ${colorClass} cursor-pointer hover:shadow-sm transition-shadow`}
    >
      <p className="text-xs text-muted-foreground capitalize">{fecha.tipo} #{fecha.numero}</p>
      <p className="text-sm font-medium truncate">{fecha.titulo}</p>
      <p className="text-xs text-muted-foreground">{fecha.materia_id.slice(0, 8)}</p>
    </div>
  );
}
