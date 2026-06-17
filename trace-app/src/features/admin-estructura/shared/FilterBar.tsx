import { useCallback } from "react";
import { cn } from "@/lib/utils";

type FilterConfig = {
  key: string;
  label: string;
  type: "text" | "select" | "date";
  options?: { label: string; value: string }[];
};

type FilterBarProps = {
  filters: FilterConfig[];
  onFilter: (values: Record<string, string>) => void;
  values: Record<string, string>;
  className?: string;
};

export function FilterBar({ filters, onFilter, values, className }: FilterBarProps) {
  const handleChange = useCallback(
    (key: string, value: string) => {
      onFilter({ ...values, [key]: value });
    },
    [onFilter, values],
  );

  const handleClear = useCallback(() => {
    const cleared: Record<string, string> = {};
    filters.forEach((f) => (cleared[f.key] = ""));
    onFilter(cleared);
  }, [filters, onFilter]);

  return (
    <div className={cn("flex flex-wrap gap-4 items-end", className)}>
      {filters.map((filter) => {
        const inputId = `filter-${filter.key}`;
        return (
          <div key={filter.key} className="flex flex-col gap-xs">
            <label htmlFor={inputId} className="font-label-sm text-label-sm text-on-surface">{filter.label}</label>
            {filter.type === "text" && (
              <input
                id={inputId}
                type="text"
                value={values[filter.key] ?? ""}
                onChange={(e) => handleChange(filter.key, e.target.value)}
                className="h-10 w-48 rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
              />
            )}
            {filter.type === "select" && (
              <select
                id={inputId}
                value={values[filter.key] ?? ""}
                onChange={(e) => handleChange(filter.key, e.target.value)}
                className="h-10 w-48 rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Todos</option>
                {filter.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            )}
            {filter.type === "date" && (
              <input
                id={inputId}
                type="date"
                value={values[filter.key] ?? ""}
                onChange={(e) => handleChange(filter.key, e.target.value)}
                className="h-10 w-48 rounded border border-outline-variant bg-white px-3 py-2 text-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
              />
            )}
          </div>
        );
      })}
      {filters.length > 0 && (
        <button
          onClick={handleClear}
          className="h-10 px-3 text-label-sm text-secondary hover:text-on-surface transition-colors"
        >
          Limpiar
        </button>
      )}
    </div>
  );
}

export type { FilterConfig };
