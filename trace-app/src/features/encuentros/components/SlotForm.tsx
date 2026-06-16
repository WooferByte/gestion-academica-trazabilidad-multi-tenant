import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { SlotFormData } from "@/features/encuentros/types";

interface SelectOption {
  id: string;
  nombre: string;
}

const slotSchema = z.object({
  asignacion_id: z.string().optional(),
  materia_id: z.string().min(1, "La materia es obligatoria"),
  titulo: z.string().min(1, "El título es obligatorio"),
  hora: z.string().regex(/^\d{2}:\d{2}$/, "Formato HH:MM requerido"),
  dia_semana: z.string().min(1, "El día es obligatorio"),
  fecha_inicio: z.string().min(1, "La fecha de inicio es obligatoria"),
  cant_semanas: z.coerce.number().int().min(0).default(0),
  fecha_unica: z.string().optional().nullable(),
  meet_url: z.string().optional().nullable(),
});

interface SlotFormProps {
  initialData?: Partial<SlotFormData>;
  onSubmit: (data: SlotFormData) => void;
  isPending?: boolean;
}

const DIAS_SEMANA = [
  { value: "Lunes", label: "Lunes" },
  { value: "Martes", label: "Martes" },
  { value: "Miercoles", label: "Miércoles" },
  { value: "Jueves", label: "Jueves" },
  { value: "Viernes", label: "Viernes" },
  { value: "Sabado", label: "Sábado" },
];

export function SlotForm({ initialData, onSubmit, isPending }: SlotFormProps) {
  const { data: materiasData } = useQuery({
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

  const materias = useMemo(() => materiasData ?? [], [materiasData]);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SlotFormData>({
    resolver: zodResolver(slotSchema),
    defaultValues: {
      cant_semanas: 0,
      ...initialData,
    },
  });

  const cantSemanas = watch("cant_semanas");
  const isRecurrente = cantSemanas > 0;

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
        <label className="block text-sm font-medium mb-1">Materia *</label>
        <select
          {...register("materia_id")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        >
          <option value="">Seleccionar materia</option>
          {materias.map((m) => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
        {errors.materia_id && (
          <p className="text-sm text-destructive mt-1">{errors.materia_id.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Hora *</label>
        <input
          type="time"
          {...register("hora")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {errors.hora && (
          <p className="text-sm text-destructive mt-1">{errors.hora.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Día de Semana *</label>
          <select
            {...register("dia_semana")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          >
            <option value="">Seleccionar día</option>
            {DIAS_SEMANA.map((d) => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
          {errors.dia_semana && (
            <p className="text-sm text-destructive mt-1">{errors.dia_semana.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Fecha Inicio *</label>
          <input
            type="date"
            {...register("fecha_inicio")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
          {errors.fecha_inicio && (
            <p className="text-sm text-destructive mt-1">{errors.fecha_inicio.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Cantidad de Semanas</label>
          <input
            type="number"
            min="0"
            {...register("cant_semanas")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
          />
          <p className="text-xs text-on-surface-variant mt-1">
            {isRecurrente ? "Slot recurrente semanal" : "0 = Slot único"}
          </p>
        </div>

        {!isRecurrente && (
          <div>
            <label className="block text-sm font-medium mb-1">Fecha Única</label>
            <input
              type="date"
              {...register("fecha_unica")}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Enlace de Videoconferencia</label>
        <input
          type="url"
          placeholder="https://meet.google.com/..."
          {...register("meet_url")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
      </div>

      <div className="flex gap-2 pt-4">
        <button
          type="submit"
          disabled={isPending}
          className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isPending ? "Guardando..." : "Guardar Slot"}
        </button>
      </div>
    </form>
  );
}
