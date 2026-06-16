import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { AvisoFormData } from "@/features/avisos/types";

const avisoSchema = z.object({
  alcance: z.string().min(1, "El alcance es obligatorio"),
  materia_id: z.string().optional(),
  cohorte_id: z.string().optional(),
  rol_destino: z.string().optional(),
  severidad: z.string().min(1, "La severidad es obligatoria"),
  titulo: z.string().min(1, "El título es obligatorio"),
  cuerpo: z.string().min(1, "El cuerpo es obligatorio"),
  inicio_vigencia: z.string().min(1, "La fecha de inicio es obligatoria"),
  fin_vigencia: z.string().min(1, "La fecha de fin es obligatoria"),
  orden: z.coerce.number().int().default(0),
  requiere_ack: z.boolean().default(false),
});

interface AvisoFormProps {
  initialData?: Partial<AvisoFormData>;
  onSubmit: (data: AvisoFormData) => void;
  isPending?: boolean;
}

/** Minimal interface for select options from admin endpoints */
interface SelectOption {
  id: string;
  nombre: string;
}

export function AvisoForm({ initialData, onSubmit, isPending }: AvisoFormProps) {
  const { data: materiasData, isError: materiasError } = useQuery({
    queryKey: ["materias", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/materias");
        return (res.data?.items ?? []) as SelectOption[];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const { data: cohortesData, isError: cohortesError } = useQuery({
    queryKey: ["cohortes", "select"],
    queryFn: async () => {
      try {
        const res = await api.get("/admin/cohortes");
        return (res.data?.items ?? []) as SelectOption[];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  const materias = useMemo(() => materiasData ?? [], [materiasData]);
  const cohortes = useMemo(() => cohortesData ?? [], [cohortesData]);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AvisoFormData>({
    resolver: zodResolver(avisoSchema),
    defaultValues: {
      alcance: "Global",
      severidad: "Info",
      orden: 0,
      requiere_ack: false,
      ...initialData,
    },
  });

  const alcance = watch("alcance");

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Título *</label>
        <input
          {...register("titulo")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {errors.titulo && (
          <p className="text-sm text-destructive mt-1">{errors.titulo.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Cuerpo *</label>
        <textarea
          {...register("cuerpo")}
          rows={4}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {errors.cuerpo && (
          <p className="text-sm text-destructive mt-1">{errors.cuerpo.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Alcance *</label>
          <select
            {...register("alcance")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="Global">Global</option>
            <option value="PorMateria">Por Materia</option>
            <option value="PorCohorte">Por Cohorte</option>
            <option value="PorRol">Por Rol</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Severidad *</label>
          <select
            {...register("severidad")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="Info">Info</option>
            <option value="Advertencia">Advertencia</option>
            <option value="Urgente">Urgente</option>
          </select>
        </div>
      </div>

      {alcance === "PorMateria" && (
        <div>
          <label className="block text-sm font-medium mb-1">Materia *</label>
          {materias.length > 0 ? (
            <select
              {...register("materia_id")}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar materia</option>
              {materias.map((m) => (
                <option key={m.id} value={m.id}>{m.nombre}</option>
              ))}
            </select>
          ) : (
            <input
              {...register("materia_id")}
              placeholder="ID de la materia"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          )}
        </div>
      )}

      {alcance === "PorCohorte" && (
        <div>
          <label className="block text-sm font-medium mb-1">Cohorte *</label>
          {cohortes.length > 0 ? (
            <select
              {...register("cohorte_id")}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccionar cohorte</option>
              {cohortes.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          ) : (
            <input
              {...register("cohorte_id")}
              placeholder="ID de la cohorte"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          )}
        </div>
      )}

      {alcance === "PorRol" && (
        <div>
          <label className="block text-sm font-medium mb-1">Rol Destino</label>
          <select
            {...register("rol_destino")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccionar</option>
            <option value="PROFESOR">Profesor</option>
            <option value="TUTOR">Tutor</option>
            <option value="COORDINADOR">Coordinador</option>
            <option value="NEXO">Nexo</option>
          </select>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Inicio Vigencia *</label>
          <input
            type="datetime-local"
            {...register("inicio_vigencia")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Fin Vigencia *</label>
          <input
            type="datetime-local"
            {...register("fin_vigencia")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Orden</label>
          <input
            type="number"
            {...register("orden")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
          <p className="text-xs text-on-surface-variant mt-1">
            Prioridad de visualización (menor número = más arriba)
          </p>
        </div>
        <div className="flex items-center gap-2 pt-6">
          <input type="checkbox" {...register("requiere_ack")} id="requiere_ack" />
          <label htmlFor="requiere_ack" className="text-sm">
            Requiere confirmación de lectura
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {isPending ? "Guardando..." : "Guardar"}
      </button>
    </form>
  );
}
