import { useState } from "react";
import { showToast } from "@/components/ui/Toast";

interface ComentarioFormProps {
  onSubmit: (texto: string) => Promise<void>;
  isSubmitting?: boolean;
}

export function ComentarioForm({ onSubmit, isSubmitting }: ComentarioFormProps) {
  const [texto, setTexto] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!texto.trim()) {
      showToast("El comentario no puede estar vacío", "error");
      return;
    }
    await onSubmit(texto.trim());
    setTexto("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Escribí un comentario..."
        rows={3}
        className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
      />
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting || !texto.trim()}
          className="px-4 py-2 text-sm rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isSubmitting ? "Enviando..." : "Enviar Comentario"}
        </button>
      </div>
    </form>
  );
}
