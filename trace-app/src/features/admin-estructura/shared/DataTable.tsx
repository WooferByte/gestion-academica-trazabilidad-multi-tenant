import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/Skeleton";
import { EmptyState } from "./EmptyState";
import type { SortDir } from "./useDataTable";

type Column<T> = {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
};

type DataTableProps<T> = {
  columns: Column<T>[];
  data: T[];
  isLoading: boolean;
  sortKey?: string | null;
  sortDir?: SortDir | null;
  onSort?: (key: string) => void;
  page?: number;
  pageSize?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  keyExtractor: (item: T) => string | number;
  emptyMessage?: string;
  className?: string;
};

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  isLoading,
  sortKey,
  sortDir,
  onSort,
  page = 1,
  pageSize = 10,
  totalPages = 1,
  onPageChange,
  keyExtractor,
  emptyMessage = "No se encontraron registros",
  className,
}: DataTableProps<T>) {
  const renderSortIcon = (key: string) => {
    if (sortKey !== key) {
      return <ChevronUp className="size-4 text-secondary opacity-0 group-hover:opacity-100 transition-opacity" />;
    }
    return sortDir === "asc" ? (
      <ChevronUp className="size-4 text-primary" />
    ) : (
      <ChevronDown className="size-4 text-primary" />
    );
  };

  if (isLoading) {
    return (
      <div className={cn("rounded-lg border border-outline-variant bg-white", className)}>
        {Array.from({ length: pageSize }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "flex items-center gap-4 px-4 py-3",
              i > 0 && "border-t border-outline-variant",
            )}
          >
            {columns.map((col) => (
              <Skeleton key={col.key} className="h-5 flex-1" />
            ))}
          </div>
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={cn("rounded-lg border border-outline-variant bg-white", className)}>
        <EmptyState message={emptyMessage} />
      </div>
    );
  }

  return (
    <div className={cn("rounded-lg border border-outline-variant bg-white", className)}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    "px-4 py-3 text-left font-label-sm text-label-sm text-on-surface-variant",
                    col.sortable && "cursor-pointer select-none group hover:text-on-surface",
                  )}
                  onClick={() => {
                    if (col.sortable && onSort) onSort(col.key);
                  }}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && renderSortIcon(col.key)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr
                key={keyExtractor(item)}
                className="border-b border-outline-variant last:border-b-0 hover:bg-surface-container-hover transition-colors"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-body-md text-on-surface">
                    {col.render ? col.render(item) : String(item[col.key] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {onPageChange && totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-outline-variant px-4 py-3">
          <span className="text-body-sm text-on-surface-variant">
            Página {page} de {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              className="flex items-center justify-center size-8 rounded hover:bg-surface-container disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="size-4" />
            </button>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              className="flex items-center justify-center size-8 rounded hover:bg-surface-container disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="size-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export type { Column, DataTableProps };
