import { useState, useMemo, useCallback } from "react";

type SortDir = "asc" | "desc";

type UseDataTableOptions = {
  initialPage?: number;
  initialPageSize?: number;
  initialSortKey?: string;
  initialSortDir?: SortDir;
  totalItems?: number;
};

type UseDataTableReturn = {
  page: number;
  pageSize: number;
  sortKey: string | null;
  sortDir: SortDir | null;
  totalPages: number;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setSort: (key: string) => void;
  reset: () => void;
};

export function useDataTable({
  initialPage = 1,
  initialPageSize = 10,
  initialSortKey,
  initialSortDir,
  totalItems = 0,
}: UseDataTableOptions = {}): UseDataTableReturn {
  const [page, setPageState] = useState(initialPage);
  const [pageSize, setPageSizeState] = useState(initialPageSize);
  const [sortKey, setSortKey] = useState<string | null>(initialSortKey ?? null);
  const [sortDir, setSortDir] = useState<SortDir | null>(initialSortDir ?? null);

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(totalItems / pageSize)),
    [totalItems, pageSize],
  );

  const setPage = useCallback(
    (newPage: number) => {
      setPageState(Math.max(1, Math.min(newPage, totalPages)));
    },
    [totalPages],
  );

  const setPageSize = useCallback(
    (size: number) => {
      setPageSizeState(size);
      setPageState(1);
    },
    [],
  );

  const setSort = useCallback((key: string) => {
    setSortKey((prev) => {
      if (prev === key) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        return prev;
      }
      setSortDir("asc");
      return key;
    });
  }, []);

  const reset = useCallback(() => {
    setPageState(initialPage);
    setPageSizeState(initialPageSize);
    setSortKey(initialSortKey ?? null);
    setSortDir(initialSortDir ?? null);
  }, [initialPage, initialPageSize, initialSortKey, initialSortDir]);

  return {
    page,
    pageSize,
    sortKey,
    sortDir,
    totalPages,
    setPage,
    setPageSize,
    setSort,
    reset,
  };
}

export type { SortDir, UseDataTableOptions, UseDataTableReturn };
