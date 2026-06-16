import type { ComentarioResponse } from "@/api/types";

interface ComentarioTimelineProps {
  comentarios: ComentarioResponse[];
}

export function ComentarioTimeline({ comentarios }: ComentarioTimelineProps) {
  if (comentarios.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        No hay comentarios aún
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {[...comentarios]
        .sort((a, b) => new Date(a.creado_at).getTime() - new Date(b.creado_at).getTime())
        .map((comentario) => (
          <div key={comentario.id} className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium text-primary">
              {(comentario.autor_nombre ?? "U").charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">
                  {comentario.autor_nombre ?? "Usuario"}
                </span>
                <span className="text-xs text-muted-foreground">
                  {new Date(comentario.creado_at).toLocaleString("es-AR")}
                </span>
              </div>
              <p className="text-sm text-on-surface">{comentario.texto}</p>
            </div>
          </div>
        ))}
    </div>
  );
}
