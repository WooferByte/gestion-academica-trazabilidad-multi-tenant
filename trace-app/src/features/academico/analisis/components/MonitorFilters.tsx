import { Input } from "@/components/ui/Input";

interface MonitorFiltersValue {
  q: string;
  fecha_desde: string;
  fecha_hasta: string;
}

type MonitorFiltersProps = {
  filters: MonitorFiltersValue;
  onChange: (filters: MonitorFiltersValue) => void;
  showDates?: boolean;
};

export function MonitorFilters({ filters, onChange, showDates = false }: MonitorFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-md">
      <div className="flex-1 min-w-[200px]">
        <label className="mb-xs block font-label-sm text-label-sm text-on-surface-variant">
          Buscar
        </label>
        <Input
          placeholder="Nombre, apellido..."
          value={filters.q}
          onChange={(e) => onChange({ ...filters, q: e.target.value })}
        />
      </div>
      {showDates && (
        <>
          <div>
            <label className="mb-xs block font-label-sm text-label-sm text-on-surface-variant">
              Desde
            </label>
            <Input
              type="date"
              value={filters.fecha_desde}
              onChange={(e) => onChange({ ...filters, fecha_desde: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-xs block font-label-sm text-label-sm text-on-surface-variant">
              Hasta
            </label>
            <Input
              type="date"
              value={filters.fecha_hasta}
              onChange={(e) => onChange({ ...filters, fecha_hasta: e.target.value })}
            />
          </div>
        </>
      )}
    </div>
  );
}
