import { useQuery } from "@tanstack/react-query";
import { Dialog } from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import api from "@/api/client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import type { CreateFacturaDTO } from "../types/factura";

const schema = z.object({
  usuario_id: z.string().min(1, "Seleccioná un usuario"),
  periodo: z.string().min(1, "Seleccioná un período"),
  detalle: z.string().min(1, "El detalle es requerido"),
});

type FormValues = z.infer<typeof schema>;

type UsuarioOption = {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
};

type CrearFacturaDialogProps = {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateFacturaDTO) => void;
  isPending: boolean;
};

function useUsuarios() {
  return useQuery({
    queryKey: ["admin-usuarios", "all"],
    queryFn: () => api.get<{ items: UsuarioOption[] }>("/admin/usuarios").then((r) => r.data.items),
    staleTime: 60 * 1000,
  });
}

export function CrearFacturaDialog({ open, onClose, onSubmit, isPending }: CrearFacturaDialogProps) {
  const { data: usuarios } = useUsuarios();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { usuario_id: "", periodo: "", detalle: "" },
  });

  const handleFormSubmit = (data: FormValues) => {
    try {
      onSubmit(data as CreateFacturaDTO);
      reset();
    } catch {
      showToast("Error al crear factura", "error");
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      title="Nueva Factura"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose}>
            Cancelar
          </Button>
          <Button type="submit" form="crear-factura-form" disabled={isPending}>
            {isPending ? "Creando..." : "Crear"}
          </Button>
        </>
      }
    >
      <form id="crear-factura-form" onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="usuario_id" className="text-sm font-medium text-gray-700">
            Usuario
          </label>
          <select
            id="usuario_id"
            {...register("usuario_id")}
            className="h-10 rounded border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Seleccioná un usuario</option>
            {usuarios?.map((u) => (
              <option key={u.id} value={u.id}>
                {u.nombre} {u.apellido} ({u.email})
              </option>
            ))}
          </select>
          {errors.usuario_id && (
            <p className="text-sm text-red-500">{errors.usuario_id.message}</p>
          )}
        </div>
        <Input
          label="Período"
          type="month"
          {...register("periodo")}
          error={errors.periodo?.message}
        />
        <div className="flex flex-col gap-1">
          <label htmlFor="detalle" className="text-sm font-medium text-gray-700">
            Detalle
          </label>
          <textarea
            id="detalle"
            {...register("detalle")}
            className="h-24 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errors.detalle && (
            <p className="text-sm text-red-500">{errors.detalle.message}</p>
          )}
        </div>
      </form>
    </Dialog>
  );
}
