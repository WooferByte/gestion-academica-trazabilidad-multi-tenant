import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { AsignacionResponse } from "@/api/types";

interface AsignacionFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  initialData?: AsignacionResponse | null;
  isPending?: boolean;
}

export function AsignacionFormDialog({
  isOpen,
  onClose,
  onSave,
  initialData,
  isPending,
}: AsignacionFormDialogProps) {
  const [usuarioId, setUsuarioId] = useState(initialData?.usuario_id ?? "");
  const [rol, setRol] = useState(initialData?.rol ?? "");
  const [materiaId, setMateriaId] = useState(initialData?.materia_id ?? "");
  const [carreraId, setCarreraId] = useState(initialData?.carrera_id ?? "");
  const [cohorteId, setCohorteId] = useState(initialData?.cohorte_id ?? "");
  const [comisiones, setComisiones] = useState(initialData?.comisiones?.join(", ") ?? "");
  const [responsableId, setResponsableId] = useState(initialData?.responsable_id ?? "");
  const [desde, setDesde] = useState(initialData?.desde ?? "");
  const [hasta, setHasta] = useState(initialData?.hasta ?? "");

  useEffect(() => {
    setUsuarioId(initialData?.usuario_id ?? "");
    setRol(initialData?.rol ?? "");
    setMateriaId(initialData?.materia_id ?? "");
    setCarreraId(initialData?.carrera_id ?? "");
    setCohorteId(initialData?.cohorte_id ?? "");
    setComisiones(initialData?.comisiones?.join(", ") ?? "");
    setResponsableId(initialData?.responsable_id ?? "");
    setDesde(initialData?.desde ?? "");
    setHasta(initialData?.hasta ?? "");
  }, [initialData]);

  const { data: usuarios } = useQuery({
    queryKey: ["usuarios", "form"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/usuarios");
        return (res.data?.items ?? []) as { id: string; nombre: string; apellido: string; email: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: materias } = useQuery({
    queryKey: ["materias", "form"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/materias");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: carreras } = useQuery({
    queryKey: ["carreras", "form"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/carreras");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortes } = useQuery({
    queryKey: ["cohortes", "form"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/cohortes");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const usuariosList = useMemo(() => usuarios ?? [], [usuarios]);
  const materiasList = useMemo(() => materias ?? [], [materias]);
  const carrerasList = useMemo(() => carreras ?? [], [carreras]);
  const cohortesList = useMemo(() => cohortes ?? [], [cohortes]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      usuario_id: usuarioId,
      rol,
      materia_id: materiaId || null,
      carrera_id: carreraId || null,
      cohorte_id: cohorteId || null,
      comisiones: comisiones
        ? comisiones.split(",").map((c) => c.trim()).filter(Boolean)
        : null,
      responsable_id: responsableId || null,
      desde: desde || null,
      hasta: hasta || null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-surface rounded-lg shadow-lg w-full max-w-lg mx-4 p-6">
        <h2 className="text-lg font-semibold mb-4">
          {initialData ? "Editar Asignación" : "Nueva Asignación"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Usuario</label>
            <select
              value={usuarioId}
              onChange={(e) => setUsuarioId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              required
            >
              <option value="">Seleccionar usuario</option>
              {usuariosList.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nombre} {u.apellido} ({u.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Rol</label>
            <select
              value={rol}
              onChange={(e) => setRol(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              required
            >
              <option value="">Seleccionar</option>
              <option value="PROFESOR">Profesor</option>
              <option value="TUTOR">Tutor</option>
              <option value="JTP">JTP</option>
              <option value="AYUDANTE">Ayudante</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Materia</label>
            <select
              value={materiaId}
              onChange={(e) => setMateriaId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar</option>
              {materiasList.map((m) => (
                <option key={m.id} value={m.id}>{m.nombre}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Carrera</label>
            <select
              value={carreraId}
              onChange={(e) => setCarreraId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar</option>
              {carrerasList.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Cohorte</label>
            <select
              value={cohorteId}
              onChange={(e) => setCohorteId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar</option>
              {cohortesList.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Comisiones</label>
            <input
              value={comisiones}
              onChange={(e) => setComisiones(e.target.value)}
              placeholder="Ej: ComA, ComB (separadas por coma)"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Responsable</label>
            <select
              value={responsableId}
              onChange={(e) => setResponsableId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar</option>
              {usuariosList.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nombre} {u.apellido}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Desde</label>
              <input
                type="date"
                value={desde}
                onChange={(e) => setDesde(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Hasta</label>
              <input
                type="date"
                value={hasta}
                onChange={(e) => setHasta(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-md border border-border hover:bg-surface-dimmed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {isPending ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
