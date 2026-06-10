import type { Actividad } from "@/api/types";
import { Button } from "@/components/ui/Button";

type ActivitySelectorProps = {
  actividades: Actividad[];
  selectedIds: string[];
  onToggle: (id: string) => void;
  onView: () => void;
};

export function ActivitySelector({
  actividades,
  selectedIds,
  onToggle,
  onView,
}: ActivitySelectorProps) {
  return (
    <div className="space-y-md">
      <h3 className="font-label-lg text-label-lg text-on-surface">Actividades</h3>

      <div className="flex flex-wrap gap-sm">
        {actividades.map((act) => (
          <label
            key={act.id}
            className="flex cursor-pointer items-center gap-xs rounded-lg border border-outline-variant px-md py-sm transition-colors hover:bg-surface-container has-[:checked]:border-primary has-[:checked]:bg-primary/5"
          >
            <input
              type="checkbox"
              checked={selectedIds.includes(act.id)}
              onChange={() => onToggle(act.id)}
              className="h-4 w-4 accent-primary"
            />
            <span className="font-body-sm text-body-sm text-on-surface">{act.nombre}</span>
          </label>
        ))}
      </div>

      <Button onClick={onView} disabled={selectedIds.length === 0}>
        Ver notas
      </Button>
    </div>
  );
}
