import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/client";

interface DelegarDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onDelegar: (usuarioId: string) => void;
  onElevar: () => void;
  isSubmitting?: boolean;
}

export function DelegarDialog({ isOpen, onClose, onDelegar, onElevar, isSubmitting }: DelegarDialogProps) {
  const [usuarioId, setUsuarioId] = useState("");

  const { data: usuarios } = useQuery({
    queryKey: ["delegar-usuarios"],
    queryFn: async () => {
      try {
        const res = await api.get<{ items: { id: string; nombre: string; apellido: string }[] }>("/admin/usuarios");
        return res.data.items ?? [];
      } catch {
        return [];
      }
    },
    staleTime: 60000,
    retry: false,
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-surface rounded-lg shadow-xl border border-border w-full max-w-md p-6 space-y-4">
        <h2 className="text-lg font-semibold">Delegar o Elevar Tarea</h2>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">
              Delegar a
            </label>
            <select
              value={usuarioId}
              onChange={(e) => setUsuarioId(e.target.value)}
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Seleccioná un usuario</option>
              {usuarios?.map((u) => (
                <option key={u.id} value={u.id}>{u.nombre} {u.apellido}</option>
              ))}
            </select>
          </div>

          <button
            type="button"
            disabled={isSubmitting || !usuarioId.trim()}
            onClick={() => onDelegar(usuarioId.trim())}
            className="w-full px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? "Delegando..." : "Delegar"}
          </button>

          <div className="border-t border-border pt-3">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={onElevar}
              className="w-full px-4 py-2 text-sm rounded-md bg-amber-100 text-amber-800 hover:bg-amber-200 disabled:opacity-50"
            >
              {isSubmitting ? "Elevando..." : "Elevar a Coordinación"}
            </button>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-md border border-border hover:bg-accent"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
