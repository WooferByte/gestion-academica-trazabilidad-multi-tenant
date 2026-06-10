import { Button } from "@/components/ui/Button";
import type { Actividad } from "@/api/types";

type PreviewStepProps = {
  actividades: Actividad[];
  selectedIds: string[];
  onToggle: (id: string) => void;
  isConfirming: boolean;
  onConfirm: () => void;
  onBack: () => void;
  error?: string | null;
};

export function PreviewStep({
  actividades,
  selectedIds,
  onToggle,
  isConfirming,
  onConfirm,
  onBack,
  error,
}: PreviewStepProps) {
  return (
    <div className="space-y-md">
      <h3 className="font-label-lg text-label-lg text-on-surface">
        Actividades detectadas
      </h3>

      <div className="space-y-sm">
        {actividades.map((act) => (
          <label
            key={act.id + act.nombre}
            className="flex items-center gap-md rounded-lg border border-outline-variant px-md py-sm transition-colors hover:bg-surface-container"
          >
            <input
              type="checkbox"
              checked={selectedIds.includes(act.nombre)}
              onChange={() => onToggle(act.nombre)}
              className="h-4 w-4 accent-primary"
            />
            <div className="flex flex-1 items-center justify-between">
              <span className="font-body-md text-body-md text-on-surface">
                {act.nombre}
              </span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                {act.tipo}
              </span>
            </div>
          </label>
        ))}
      </div>

      {error && (
        <div className="rounded-lg border border-error bg-error-container px-md py-sm text-body-sm text-error">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          Volver
        </Button>
        <Button onClick={onConfirm} disabled={selectedIds.length === 0 || isConfirming}>
          {isConfirming ? "Importando..." : `Importar (${selectedIds.length} actividades)`}
        </Button>
      </div>
    </div>
  );
}
