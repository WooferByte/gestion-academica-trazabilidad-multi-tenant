import { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog } from "@/components/ui/Dialog";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import { useCrearUsuario, useActualizarUsuario } from "../hooks/useUsuarios";
import type { Usuario } from "../types/usuario";

const createSchema = z.object({
  nombre: z.string().min(1, "El nombre es requerido"),
  apellido: z.string().min(1, "El apellido es requerido"),
  email: z.string().email("Email inválido"),
  password: z.string().min(4, "La contraseña debe tener al menos 4 caracteres"),
  dni: z.string().optional(),
  cuil: z.string().optional(),
  banco: z.string().optional(),
  cbu: z.string().optional(),
  alias_cbu: z.string().optional(),
  regional: z.string().optional(),
  legajo: z.string().optional(),
  facturador: z.boolean().optional(),
});

const editSchema = z.object({
  nombre: z.string().optional(),
  apellido: z.string().optional(),
  email: z.string().email("Email inválido").optional(),
  dni: z.string().optional(),
  cuil: z.string().optional(),
  banco: z.string().optional(),
  cbu: z.string().optional(),
  alias_cbu: z.string().optional(),
  regional: z.string().optional(),
  legajo: z.string().optional(),
  facturador: z.boolean().optional(),
});

type CreateFormValues = z.infer<typeof createSchema>;
type EditFormValues = z.infer<typeof editSchema>;

type UsuarioFormModalProps = {
  open: boolean;
  onClose: () => void;
  usuario?: Usuario | null;
};

export function UsuarioFormModal({ open, onClose, usuario }: UsuarioFormModalProps) {
  const isEdit = !!usuario;
  const schema = useMemo(() => (isEdit ? editSchema : createSchema), [isEdit]);
  const crearMutation = useCrearUsuario();
  const actualizarMutation = useActualizarUsuario();

  type FormValues = z.infer<typeof schema>;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: isEdit
      ? { nombre: "", apellido: "", email: "" }
      : { nombre: "", apellido: "", email: "", password: "", facturador: false },
  });

  useEffect(() => {
    if (open && usuario) {
      reset({
        nombre: usuario.nombre || "",
        apellido: usuario.apellido || "",
        email: usuario.email || "",
        banco: usuario.banco || "",
        regional: usuario.regional || "",
        legajo: usuario.legajo || "",
        facturador: usuario.facturador,
      });
    }
    if (open && !usuario) {
      reset({
        nombre: "",
        apellido: "",
        email: "",
        password: "",
        dni: "",
        cuil: "",
        banco: "",
        cbu: "",
        alias_cbu: "",
        regional: "",
        legajo: "",
        facturador: false,
      });
    }
  }, [open, usuario, reset]);

  const onSubmit = async (rawData: FormValues) => {
    try {
      const data = { ...rawData } as Record<string, unknown>;
      // Strip empty optional fields
      for (const key of Object.keys(data)) {
        if (data[key] === "" || data[key] === undefined) {
          delete data[key];
        }
      }
      // Backend UsuarioUpdate doesn't accept email - remove it on edit
      if (isEdit) {
        delete data.email;
        delete data.password;
      }
      if (isEdit && usuario) {
        await actualizarMutation.mutateAsync({ id: usuario.id, data: data as Parameters<typeof actualizarMutation.mutateAsync>[0]["data"] });
      } else {
        await crearMutation.mutateAsync(data as Parameters<typeof crearMutation.mutateAsync>[0]);
      }
      reset();
      onClose();
      showToast(isEdit ? "Usuario actualizado" : "Usuario creado", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error al guardar el usuario";
      showToast(msg, "error");
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title={isEdit ? "Editar usuario" : "Nuevo usuario"}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit(onSubmit)} disabled={isSubmitting}>
            {isSubmitting ? "Guardando..." : isEdit ? "Actualizar" : "Crear"}
          </Button>
        </>
      }
    >
      <form id="usuario-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Nombre"
            placeholder="Ej: Juan"
            {...register("nombre")}
            error={(errors as Record<string, { message?: string }>).nombre?.message}
          />
          <Input
            label="Apellido"
            placeholder="Ej: Pérez"
            {...register("apellido")}
            error={(errors as Record<string, { message?: string }>).apellido?.message}
          />
        </div>
        <Input
          label="Email"
          type="email"
          placeholder="ejemplo@email.com"
          {...register("email")}
          error={(errors as Record<string, { message?: string }>).email?.message}
        />
        {!isEdit && (
          <Input
            label="Contraseña"
            type="password"
            placeholder="Mínimo 4 caracteres"
            {...register("password")}
            error={(errors as Record<string, { message?: string }>).password?.message}
          />
        )}
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="DNI"
            placeholder={isEdit ? "Dato cifrado" : "Ej: 12345678"}
            {...register("dni")}
            error={(errors as Record<string, { message?: string }>).dni?.message}
          />
          <Input
            label="CUIL"
            placeholder={isEdit ? "Dato cifrado" : "Ej: 20-12345678-9"}
            {...register("cuil")}
            error={(errors as Record<string, { message?: string }>).cuil?.message}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Banco"
            placeholder="Ej: Banco Nación"
            {...register("banco")}
            error={(errors as Record<string, { message?: string }>).banco?.message}
          />
          <Input
            label="Legajo"
            placeholder="Ej: LEG-001"
            {...register("legajo")}
            error={(errors as Record<string, { message?: string }>).legajo?.message}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="CBU"
            placeholder={isEdit ? "Dato cifrado" : "Ej: 1234567890123456789012"}
            {...register("cbu")}
            error={(errors as Record<string, { message?: string }>).cbu?.message}
          />
          <Input
            label="Alias CBU"
            placeholder={isEdit ? "Dato cifrado" : "Ej: juan.perez.cbu"}
            {...register("alias_cbu")}
            error={(errors as Record<string, { message?: string }>).alias_cbu?.message}
          />
        </div>
        <Input
          label="Regional"
          placeholder="Ej: Córdoba"
          {...register("regional")}
          error={(errors as Record<string, { message?: string }>).regional?.message}
        />
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="facturador"
            className="size-4 rounded border-outline-variant"
            {...register("facturador")}
          />
          <label htmlFor="facturador" className="font-label-md text-label-md text-on-surface">
            Facturador
          </label>
        </div>
      </form>
    </Dialog>
  );
}
