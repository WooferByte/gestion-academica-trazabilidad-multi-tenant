import { useState } from "react";
import type { InstanciaEncuentroResponse, InstanciaEncuentroUpdate } from "@/api/types";

interface InstanciaEditModalProps {
  instancia: InstanciaEncuentroResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, data: InstanciaEncuentroUpdate) => void;
  isPending?: boolean;
}

export function InstanciaEditModal({ instancia, isOpen, onClose, onSave, isPending }: InstanciaEditModalProps) {
  const [estado, setEstado] = useState(instancia?.estado || "Programado");
  const [meetUrl, setMeetUrl] = useState(instancia?.meet_url || "");
  const [videoUrl, setVideoUrl] = useState(instancia?.video_url || "");
  const [comentario, setComentario] = useState(instancia?.comentario || "");

  if (!isOpen || !instancia) return null;

  const handleSave = () => {
    onSave(instancia.id, {
      estado,
      meet_url: meetUrl || null,
      video_url: videoUrl || null,
      comentario: comentario || null,
    });
  };

  const handleClose = () => {
    setEstado(instancia.estado);
    setMeetUrl(instancia.meet_url || "");
    setVideoUrl(instancia.video_url || "");
    setComentario(instancia.comentario || "");
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={handleClose}>
      <div className="bg-surface rounded-lg border border-border p-6 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
        <h3 className="font-medium text-lg text-on-surface mb-4">
          Editar Instancia: {instancia.titulo}
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Estado</label>
            <select
              value={estado}
              onChange={(e) => setEstado(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="Programado">Programado</option>
              <option value="Realizado">Realizado</option>
              <option value="Cancelado">Cancelado</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Enlace Meet</label>
            <input
              type="url"
              value={meetUrl}
              onChange={(e) => setMeetUrl(e.target.value)}
              placeholder="https://meet.google.com/..."
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">URL de Grabación</label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://drive.google.com/..."
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Comentario</label>
            <textarea
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
              rows={3}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm rounded-md border border-border hover:bg-surface-variant"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isPending}
            className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isPending ? "Guardando..." : "Guardar"}
          </button>
        </div>
      </div>
    </div>
  );
}
