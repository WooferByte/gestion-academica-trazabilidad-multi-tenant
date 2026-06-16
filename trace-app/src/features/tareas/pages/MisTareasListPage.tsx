import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";
import { useMisTareas } from "@/features/tareas/hooks/useTareas";
import { TareaCard } from "@/features/tareas/components/TareaCard";
import { TareaEstadoBadge } from "@/features/tareas/components/TareaEstadoBadge";
import { Skeleton } from "@/components/ui/Skeleton";

const estadosFiltro = ["", "Pendiente", "En progreso", "Resuelta"];

export default function MisTareasListPage() {
  const navigate = useNavigate();
  const [filtroMateria, setFiltroMateria] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");

  const { data, isLoading } = useMisTareas(
    filtroMateria || filtroEstado
      ? {
          materia_id: filtroMateria || undefined,
          estado: filtroEstado || undefined,
        }
      : undefined,
  );

  const { data: materias } = useQuery({
    queryKey: ["materias-lista"],
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

  const items = data?.items ?? [];

  return (
    <div className="space-y-lg p-lg">
      <div className="flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Mis Tareas
        </h1>
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium mb-1">Materia</label>
          <select
            value={filtroMateria}
            onChange={(e) => setFiltroMateria(e.target.value)}
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
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Todos</option>
            {estadosFiltro.filter(Boolean).map((estado) => (
              <option key={estado} value={estado}>
                {estado === "Pendiente" ? "Pendiente" :
                 estado === "En progreso" ? "En Progreso" :
                 estado === "Resuelta" ? "Resuelta" : estado}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No tenés tareas asignadas
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((tarea) => (
            <TareaCard
              key={tarea.id}
              tarea={tarea}
              onClick={() => navigate(`/tareas/${tarea.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
