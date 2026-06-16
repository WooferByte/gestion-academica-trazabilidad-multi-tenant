import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";

interface TareasAdminFiltersProps {
  filters: {
    asignado_a: string;
    asignado_por: string;
    materia_id: string;
    estado: string;
    search: string;
  };
  onChange: (filters: TareasAdminFiltersProps["filters"]) => void;
}

const estados = ["", "Pendiente", "En progreso", "Resuelta", "Cancelada"];

export function TareasAdminFilters({ filters, onChange }: TareasAdminFiltersProps) {
  const update = (key: keyof typeof filters, value: string) => {
    onChange({ ...filters, [key]: value });
  };

  const { data: materias } = useQuery({
    queryKey: ["admin-materias-filtro"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string }[] }>("/admin/materias");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: usuarios } = useQuery({
    queryKey: ["admin-usuarios-filtro"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string; apellido: string }[] }>("/admin/usuarios");
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
        <label className="block text-sm font-medium mb-1">Asignado a</label>
        <select
          value={filters.asignado_a}
          onChange={(e) => update("asignado_a", e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {usuarios?.map((u) => (
            <option key={u.id} value={u.id}>{u.nombre} {u.apellido}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Asignado por</label>
        <select
          value={filters.asignado_por}
          onChange={(e) => update("asignado_por", e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {usuarios?.map((u) => (
            <option key={u.id} value={u.id}>{u.nombre} {u.apellido}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Materia</label>
        <select
          value={filters.materia_id}
          onChange={(e) => update("materia_id", e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todas</option>
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Estado</label>
        <select
          value={filters.estado}
          onChange={(e) => update("estado", e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          {estados.filter(Boolean).map((estado) => (
            <option key={estado} value={estado}>
              {estado === "Pendiente" ? "Pendiente" :
               estado === "En progreso" ? "En Progreso" :
               estado === "Resuelta" ? "Resuelta" :
               estado === "Cancelada" ? "Cancelada" : estado}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Buscar</label>
        <input
          value={filters.search}
          onChange={(e) => update("search", e.target.value)}
          placeholder="Título o descripción..."
          className="rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}
