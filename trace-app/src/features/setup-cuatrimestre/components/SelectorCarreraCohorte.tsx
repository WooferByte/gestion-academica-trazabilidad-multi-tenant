import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";

interface SelectorCarreraCohorteProps {
  carreraId: string;
  cohorteId: string;
  onCarreraChange: (value: string) => void;
  onCohorteChange: (value: string) => void;
}

export function SelectorCarreraCohorte({
  carreraId,
  cohorteId,
  onCarreraChange,
  onCohorteChange,
}: SelectorCarreraCohorteProps) {
  const { data: carreras } = useQuery({
    queryKey: ["carreras-lista"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string }[] }>("/admin/carreras");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortes } = useQuery({
    queryKey: ["cohortes-lista"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string; anio: number }[] }>("/admin/cohortes");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  return (
    <div className="flex flex-wrap gap-4 items-end">
      <div>
        <label className="block text-sm font-medium mb-1">Carrera</label>
        <select
          value={carreraId}
          onChange={(e) => onCarreraChange(e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todas</option>
          {carreras?.map((c) => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Cohorte</label>
        <select
          value={cohorteId}
          onChange={(e) => onCohorteChange(e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {cohortes?.map((c) => (
            <option key={c.id} value={c.id}>{c.nombre} ({c.anio})</option>
          ))}
        </select>
      </div>
    </div>
  );
}
