type MessageComposerProps = {
  destinatariosCount: number;
  asunto: string;
  onAsuntoChange: (value: string) => void;
  mensaje: string;
  onMensajeChange: (value: string) => void;
};

export function MessageComposer({
  destinatariosCount,
  asunto,
  onAsuntoChange,
  mensaje,
  onMensajeChange,
}: MessageComposerProps) {
  return (
    <div className="space-y-md">
      <div className="flex items-center gap-sm">
        <span className="material-symbols-outlined text-secondary">people</span>
        <span className="font-body-md text-body-md text-on-surface">
          {destinatariosCount} destinatario{destinatariosCount !== 1 ? "s" : ""}
        </span>
      </div>

      <input
        value={asunto}
        onChange={(e) => onAsuntoChange(e.target.value)}
        placeholder="Asunto"
        className="w-full rounded-lg border border-outline-variant bg-white px-md py-sm font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary"
      />

      <textarea
        value={mensaje}
        onChange={(e) => onMensajeChange(e.target.value)}
        placeholder="Escribí el mensaje..."
        rows={6}
        className="w-full rounded-lg border border-outline-variant bg-white px-md py-sm font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>
  );
}
