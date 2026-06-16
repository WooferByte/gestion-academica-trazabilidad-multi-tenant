import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTarea } from "@/features/tareas/hooks/useTareas";
import { useAgregarComentario } from "@/features/tareas/hooks/useTareaComentarios";
import { useActualizarTarea } from "@/features/tareas/hooks/useTareas";
import { TareaEstadoBadge } from "@/features/tareas/components/TareaEstadoBadge";
import { TareaEstadoSelect } from "@/features/tareas/components/TareaEstadoSelect";
import { ComentarioTimeline } from "@/features/tareas/components/ComentarioTimeline";
import { ComentarioForm } from "@/features/tareas/components/ComentarioForm";
import { DelegarDialog } from "@/features/tareas/components/DelegarDialog";
import { Skeleton } from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import { useAuth } from "@/features/auth/hooks/useAuth";

export default function TareaDetailPage() {
  const { tareaId } = useParams<{ tareaId: string }>();
  const navigate = useNavigate();
  const { permissions } = useAuth();
  const [delegarOpen, setDelegarOpen] = useState(false);

  const { data: tarea, isLoading } = useTarea(tareaId);
  const comentarioMutation = useAgregarComentario(tareaId);
  const actualizarMutation = useActualizarTarea();

  const isAdmin = permissions.includes("tareas:gestionar");
  const isCoordinador = permissions.includes("equipos:asignar");

  const estadosDocente = ["En progreso", "Resuelta"];
  const estadosAdmin = ["Pendiente", "En progreso", "Resuelta", "Cancelada"];
  const estadosPermitidos = isAdmin || isCoordinador ? estadosAdmin : estadosDocente;

  const handleAgregarComentario = async (texto: string) => {
    await comentarioMutation.mutateAsync({ texto });
    showToast("Comentario agregado", "success");
  };

  const handleDelegar = async (usuarioId: string) => {
    if (!tareaId) return;
    await actualizarMutation.mutateAsync({ id: tareaId, data: { asignado_a: usuarioId } });
    showToast("Tarea delegada correctamente", "success");
    setDelegarOpen(false);
  };

  const handleElevar = async () => {
    showToast("Tarea elevada a coordinación", "success");
    setDelegarOpen(false);
  };

  if (isLoading) {
    return (
      <div className="space-y-lg p-lg">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!tarea) {
    return (
      <div className="p-lg text-center text-muted-foreground">
        Tarea no encontrada
      </div>
    );
  }

  return (
    <div className="space-y-lg p-lg max-w-3xl mx-auto">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="text-sm text-primary hover:underline"
      >
        &larr; Volver
      </button>

      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <h1 className="font-headline-md text-headline-md text-on-surface">
            Detalle de Tarea
          </h1>
          <TareaEstadoSelect
            tareaId={tarea.id}
            estadoActual={tarea.estado}
            estadosPermitidos={estadosPermitidos}
          />
        </div>
        <button
          type="button"
          onClick={() => setDelegarOpen(true)}
          className="px-4 py-2 text-sm rounded-md border border-border hover:bg-accent"
        >
          Delegar / Elevar
        </button>
      </div>

      <div className="rounded-lg border border-border bg-surface p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Asignada por: </span>
            <span className="font-medium">{tarea.asignado_por_nombre ?? tarea.asignado_por.slice(0, 8)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Asignada a: </span>
            <span className="font-medium">{tarea.asignado_a_nombre ?? tarea.asignado_a.slice(0, 8)}</span>
          </div>
          {tarea.created_at && (
            <div>
              <span className="text-muted-foreground">Creada: </span>
              <span className="font-medium">{new Date(tarea.created_at).toLocaleDateString("es-AR")}</span>
            </div>
          )}
          {tarea.updated_at && (
            <div>
              <span className="text-muted-foreground">Última actualización: </span>
              <span className="font-medium">{new Date(tarea.updated_at).toLocaleDateString("es-AR")}</span>
            </div>
          )}
        </div>
        <div>
          <p className="text-sm text-on-surface whitespace-pre-wrap">{tarea.descripcion}</p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-6 space-y-4">
        <h2 className="font-headline-sm text-headline-sm text-on-surface">
          Comentarios
        </h2>
        <ComentarioTimeline comentarios={tarea.comentarios} />
        <div className="border-t border-border pt-4">
          <ComentarioForm
            onSubmit={handleAgregarComentario}
            isSubmitting={comentarioMutation.isPending}
          />
        </div>
      </div>

      <DelegarDialog
        isOpen={delegarOpen}
        onClose={() => setDelegarOpen(false)}
        onDelegar={handleDelegar}
        onElevar={handleElevar}
        isSubmitting={actualizarMutation.isPending}
      />
    </div>
  );
}
