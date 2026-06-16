import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const guardiaSchema = z.object({
  asignacion_id: z.string().min(1, "La asignación es obligatoria"),
  materia_id: z.string().min(1, "La materia es obligatoria"),
  carrera_id: z.string().optional().nullable(),
  cohorte_id: z.string().optional().nullable(),
  dia: z.string().min(1, "El día es obligatorio"),
  horario: z.string().min(1, "El horario es obligatorio"),
  comentarios: z.string().optional().nullable(),
});

export interface GuardiaFormData {
  asignacion_id: string;
  materia_id: string;
  carrera_id?: string | null;
  cohorte_id?: string | null;
  dia: string;
  horario: string;
  comentarios?: string | null;
}

interface GuardiaFormProps {
  initialData?: Partial<GuardiaFormData>;
  onSubmit: (data: GuardiaFormData) => void;
  isPending?: boolean;
}

export function GuardiaForm({ initialData, onSubmit, isPending }: GuardiaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<GuardiaFormData>({
    resolver: zodResolver(guardiaSchema),
    defaultValues: {
      ...initialData,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Día *</label>
        <input
          type="date"
          {...register("dia")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {errors.dia && (
          <p className="text-sm text-destructive mt-1">{errors.dia.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Horario *</label>
        <input
          type="text"
          placeholder="Ej: 18:00 - 21:00"
          {...register("horario")}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        {errors.horario && (
          <p className="text-sm text-destructive mt-1">{errors.horario.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Comentarios</label>
        <textarea
          {...register("comentarios")}
          rows={3}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
      </div>

      <div className="flex gap-2 pt-4">
        <button
          type="submit"
          disabled={isPending}
          className="px-6 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isPending ? "Guardando..." : "Registrar Guardia"}
        </button>
      </div>
    </form>
  );
}
