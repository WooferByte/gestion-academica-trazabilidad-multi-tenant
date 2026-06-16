import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useAsignacionMasiva } from "@/features/equipos/hooks/useAsignacionMasiva";
import { showToast } from "@/components/ui/Toast";

export default function AsignacionMasivaPage() {
  const [usuarioIds, setUsuarioIds] = useState<string[]>([]);
  const [materiaId, setMateriaId] = useState("");
  const [carreraId, setCarreraId] = useState("");
  const [cohorteId, setCohorteId] = useState("");
  const [rol, setRol] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [error, setError] = useState("");

  const mutation = useAsignacionMasiva();

  const { data: materiasData } = useQuery({
    queryKey: ["materias", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/materias");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortesData } = useQuery({
    queryKey: ["cohortes", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/cohortes");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: carrerasData } = useQuery({
    queryKey: ["carreras", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/carreras");
        return (res.data?.items ?? []) as { id: string; nombre: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: usuariosData } = useQuery({
    queryKey: ["usuarios", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/usuarios");
        return (res.data?.items ?? []) as { id: string; nombre: string; apellido: string; email: string }[];
      } catch { return []; }
    },
    staleTime: 60000,
    retry: false,
  });

  const materias = useMemo(() => materiasData ?? [], [materiasData]);
  const cohortes = useMemo(() => cohortesData ?? [], [cohortesData]);
  const carreras = useMemo(() => carrerasData ?? [], [carrerasData]);
  const usuarios = useMemo(() => usuariosData ?? [], [usuariosData]);

  const handleAddDocente = () => {
    if (inputValue.trim() && !usuarioIds.includes(inputValue.trim())) {
      setUsuarioIds((prev) => [...prev, inputValue.trim()]);
      setInputValue("");
    }
  };

  const handleRemoveDocente = (id: string) => {
    setUsuarioIds((prev) => prev.filter((uid) => uid !== id));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (usuarioIds.length === 0) {
      setError("Seleccioná al menos un docente");
      return;
    }

    try {
      await mutation.mutateAsync({
        usuario_ids: usuarioIds,
        materia_id: materiaId || null,
        carrera_id: carreraId || null,
        cohorte_id: cohorteId || null,
        rol,
        desde: desde || null,
        hasta: hasta || null,
      });
      showToast(`Asignación masiva completada: ${usuarioIds.length} docentes`, "success");
      setUsuarioIds([]);
      setRol("");
      setDesde("");
      setHasta("");
    } catch {
      showToast("Error al realizar la asignación masiva", "error");
    }
  };

  return (
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Asignación Masiva
      </h1>

      <form onSubmit={handleSubmit} className="max-w-2xl space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Docentes</label>
          <div className="flex gap-2 mb-2">
            <select
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar docente</option>
              {usuarios.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nombre} {u.apellido} ({u.email})
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={handleAddDocente}
              className="px-3 py-2 text-sm rounded-md bg-secondary text-secondary-foreground"
            >
              Agregar
            </button>
          </div>
          {usuarioIds.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {usuarioIds.map((id) => {
                const user = usuarios.find((u) => u.id === id);
                return (
                  <span
                    key={id}
                    className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/10 text-primary text-xs"
                  >
                    {user ? `${user.nombre} ${user.apellido}` : id}
                    <button
                      type="button"
                      onClick={() => handleRemoveDocente(id)}
                      className="hover:text-destructive"
                      aria-label={`Eliminar ${id}`}
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
          )}
          {error && <p className="text-sm text-destructive mt-1">{error}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Materia</label>
          <select
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccionar</option>
            {materias.map((m) => (
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
            {carreras.map((c) => (
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
            {cohortes.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
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

        <button
          type="submit"
          disabled={mutation.isPending}
          className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {mutation.isPending ? "Asignando..." : "Asignar"}
        </button>
      </form>
    </div>
  );
}
