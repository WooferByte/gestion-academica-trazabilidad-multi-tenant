import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, renderHook, act, fireEvent } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { EmptyState } from "@/features/admin-estructura/shared/EmptyState";
import { StatusBadge } from "@/features/admin-estructura/shared/StatusBadge";
import { SearchInput } from "@/features/admin-estructura/shared/SearchInput";
import { ConfirmDialog } from "@/features/admin-estructura/shared/ConfirmDialog";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { FilterBar } from "@/features/admin-estructura/shared/FilterBar";
import { DataTable } from "@/features/admin-estructura/shared/DataTable";
import { useDataTable } from "@/features/admin-estructura/shared/useDataTable";

describe("EmptyState", () => {
  it("renders message", () => {
    renderWithProviders(<EmptyState message="No hay datos" />);
    expect(screen.getByText("No hay datos")).toBeInTheDocument();
  });

  it("renders action button when provided", () => {
    const onClick = vi.fn();
    renderWithProviders(
      <EmptyState message="Vacío" action={{ label: "Crear", onClick }} />,
    );
    const btn = screen.getByText("Crear");
    expect(btn).toBeInTheDocument();
    btn.click();
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("renders custom icon", () => {
    renderWithProviders(
      <EmptyState message="Test" icon={<span>🔍</span>} />,
    );
    expect(screen.getByText("🔍")).toBeInTheDocument();
  });
});

describe("StatusBadge", () => {
  it("renders Activo when active is true", () => {
    renderWithProviders(<StatusBadge active={true} />);
    const badge = screen.getByText("Activo");
    expect(badge.className).toContain("bg-green-100");
  });

  it("renders Inactivo when active is false", () => {
    renderWithProviders(<StatusBadge active={false} />);
    const badge = screen.getByText("Inactivo");
    expect(badge.className).not.toContain("bg-green-100");
  });

  it("renders custom label", () => {
    renderWithProviders(<StatusBadge active={true} label="Habilitado" />);
    expect(screen.getByText("Habilitado")).toBeInTheDocument();
  });
});

describe("SearchInput", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it("renders with placeholder", () => {
    renderWithProviders(
      <SearchInput value="" onChange={() => {}} placeholder="Buscar..." />,
    );
    expect(screen.getByPlaceholderText("Buscar...")).toBeInTheDocument();
  });

  it("debounces onChange", () => {
    const onChange = vi.fn();
    renderWithProviders(<SearchInput value="" onChange={onChange} debounceMs={300} />);
    const input = screen.getByPlaceholderText("Buscar...");
    fireEvent.change(input, { target: { value: "test" } });
    expect(onChange).not.toHaveBeenCalled();
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(onChange).toHaveBeenCalledWith("test");
  });

  it("cancels debounce on unmount", () => {
    const onChange = vi.fn();
    const { unmount } = renderWithProviders(
      <SearchInput value="" onChange={onChange} debounceMs={300} />,
    );
    fireEvent.change(screen.getByPlaceholderText("Buscar..."), {
      target: { value: "test" },
    });
    unmount();
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(onChange).not.toHaveBeenCalled();
  });
});

describe("ConfirmDialog", () => {
  it("renders when open", () => {
    renderWithProviders(
      <ConfirmDialog
        open={true}
        onConfirm={() => {}}
        onCancel={() => {}}
        title="Eliminar"
        message="¿Estás seguro?"
      />,
    );
    expect(screen.getByText("Eliminar")).toBeInTheDocument();
    expect(screen.getByText("¿Estás seguro?")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    renderWithProviders(
      <ConfirmDialog
        open={false}
        onConfirm={() => {}}
        onCancel={() => {}}
        title="Oculto"
        message="No visible"
      />,
    );
    expect(screen.queryByText("Oculto")).not.toBeInTheDocument();
  });

  it("calls onConfirm when confirm button clicked", () => {
    const onConfirm = vi.fn();
    renderWithProviders(
      <ConfirmDialog
        open={true}
        onConfirm={onConfirm}
        onCancel={() => {}}
        title="Confirmar"
        message="¿Proceder?"
        confirmLabel="Sí, eliminar"
      />,
    );
    screen.getByText("Sí, eliminar").click();
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("calls onCancel when cancel button clicked", () => {
    const onCancel = vi.fn();
    renderWithProviders(
      <ConfirmDialog
        open={true}
        onConfirm={() => {}}
        onCancel={onCancel}
        title="Cancelar"
        message="¿Cancelar?"
      />,
    );
    screen.getByRole("button", { name: /cancelar/i }).click();
    expect(onCancel).toHaveBeenCalledOnce();
  });
});

describe("PageHeader", () => {
  it("renders title", () => {
    renderWithProviders(<PageHeader title="Carreras" />);
    expect(screen.getByText("Carreras")).toBeInTheDocument();
  });

  it("renders action button when provided", () => {
    const onClick = vi.fn();
    renderWithProviders(
      <PageHeader title="Carreras" action={{ label: "Nueva", onClick }} />,
    );
    const btn = screen.getByText("Nueva");
    expect(btn).toBeInTheDocument();
    btn.click();
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("does not render action button when not provided", () => {
    renderWithProviders(<PageHeader title="Carreras" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});

describe("FilterBar", () => {
  const filters = [
    { key: "name", label: "Nombre", type: "text" as const },
    { key: "status", label: "Estado", type: "select" as const, options: [{ label: "Activo", value: "activo" }] },
    { key: "date", label: "Fecha", type: "date" as const },
  ];

  it("renders all filter types", () => {
    renderWithProviders(
      <FilterBar filters={filters} onFilter={() => {}} values={{}} />,
    );
    expect(screen.getByText("Nombre")).toBeInTheDocument();
    expect(screen.getByText("Estado")).toBeInTheDocument();
    expect(screen.getByText("Fecha")).toBeInTheDocument();
  });

  it("calls onFilter when text input changes", () => {
    const onFilter = vi.fn();
    renderWithProviders(
      <FilterBar filters={[filters[0]]} onFilter={onFilter} values={{}} />,
    );
    const input = screen.getByLabelText("Nombre");
    fireEvent.change(input, { target: { value: "test" } });
    expect(onFilter).toHaveBeenCalledWith({ name: "test" });
  });

  it("renders clear button and calls onFilter with empty values", () => {
    const onFilter = vi.fn();
    renderWithProviders(
      <FilterBar filters={filters} onFilter={onFilter} values={{ name: "foo" }} />,
    );
    screen.getByText("Limpiar").click();
    expect(onFilter).toHaveBeenCalledWith({ name: "", status: "", date: "" });
  });
});

describe("DataTable", () => {
  const columns = [
    { key: "name", header: "Nombre", sortable: true },
    { key: "email", header: "Email" },
  ];
  const data = [
    { name: "Juan", email: "juan@test.com" },
    { name: "Ana", email: "ana@test.com" },
  ];

  it("renders data rows", () => {
    renderWithProviders(
      <DataTable
        columns={columns}
        data={data}
        isLoading={false}
        keyExtractor={(item) => item.name}
      />,
    );
    expect(screen.getByText("Juan")).toBeInTheDocument();
    expect(screen.getByText("Ana")).toBeInTheDocument();
    expect(screen.getByText("Nombre")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
  });

  it("renders loading skeleton when isLoading", () => {
    const { container } = renderWithProviders(
      <DataTable
        columns={columns}
        data={[]}
        isLoading={true}
        keyExtractor={(item) => item.name}
      />,
    );
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders empty state when no data and not loading", () => {
    renderWithProviders(
      <DataTable
        columns={columns}
        data={[]}
        isLoading={false}
        keyExtractor={(item) => item.name}
        emptyMessage="Sin registros"
      />,
    );
    expect(screen.getByText("Sin registros")).toBeInTheDocument();
  });

  it("renders pagination when totalPages > 1 and onPageChange provided", () => {
    renderWithProviders(
      <DataTable
        columns={columns}
        data={data}
        isLoading={false}
        page={2}
        totalPages={5}
        onPageChange={() => {}}
        keyExtractor={(item) => item.name}
      />,
    );
    expect(screen.getByText("Página 2 de 5")).toBeInTheDocument();
  });

  it("calls onSort when sortable header clicked", () => {
    const onSort = vi.fn();
    renderWithProviders(
      <DataTable
        columns={columns}
        data={data}
        isLoading={false}
        onSort={onSort}
        keyExtractor={(item) => item.name}
      />,
    );
    const nombreHeader = screen.getByText("Nombre");
    nombreHeader.click();
    expect(onSort).toHaveBeenCalledWith("name");
  });

  it("renders custom cell renderer", () => {
    const cols = [
      {
        key: "name",
        header: "Name",
        render: (item: { name: string }) => <strong>{item.name}</strong>,
      },
    ];
    renderWithProviders(
      <DataTable
        columns={cols}
        data={data}
        isLoading={false}
        keyExtractor={(item) => item.name}
      />,
    );
    expect(screen.getByText("Juan").tagName).toBe("STRONG");
  });

  it("calls onPageChange when pagination buttons clicked", () => {
    const onPageChange = vi.fn();
    renderWithProviders(
      <DataTable
        columns={columns}
        data={data}
        isLoading={false}
        page={2}
        totalPages={5}
        onPageChange={onPageChange}
        keyExtractor={(item) => item.name}
      />,
    );
    const prevButton = screen.getByText("Página 2 de 5").parentElement!.querySelector("button:first-of-type")!;
    const nextButton = prevButton.nextElementSibling!;
    nextButton.click();
    expect(onPageChange).toHaveBeenCalledWith(3);
    prevButton.click();
    expect(onPageChange).toHaveBeenCalledWith(1);
  });
});

describe("useDataTable", () => {
  it("returns initial state", () => {
    const { result } = renderHook(() => useDataTable());
    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(10);
    expect(result.current.sortKey).toBeNull();
    expect(result.current.sortDir).toBeNull();
    expect(result.current.totalPages).toBe(1);
  });

  it("computes totalPages from totalItems", () => {
    const { result } = renderHook(() =>
      useDataTable({ totalItems: 25, initialPageSize: 10 }),
    );
    expect(result.current.totalPages).toBe(3);
  });

  it("setPage clamps to valid range", () => {
    const { result } = renderHook(() =>
      useDataTable({ totalItems: 25, initialPageSize: 10 }),
    );
    act(() => result.current.setPage(5));
    expect(result.current.page).toBe(3);
    act(() => result.current.setPage(0));
    expect(result.current.page).toBe(1);
  });

  it("setSort toggles direction on same key", () => {
    const { result } = renderHook(() => useDataTable());
    act(() => result.current.setSort("name"));
    expect(result.current.sortKey).toBe("name");
    expect(result.current.sortDir).toBe("asc");
    act(() => result.current.setSort("name"));
    expect(result.current.sortDir).toBe("desc");
  });

  it("setSort changes key and resets direction", () => {
    const { result } = renderHook(() => useDataTable());
    act(() => result.current.setSort("name"));
    act(() => result.current.setSort("email"));
    expect(result.current.sortKey).toBe("email");
    expect(result.current.sortDir).toBe("asc");
  });

  it("setPageSize resets to page 1", () => {
    const { result } = renderHook(() =>
      useDataTable({ totalItems: 50, initialPageSize: 10 }),
    );
    act(() => result.current.setPage(3));
    act(() => result.current.setPageSize(20));
    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(20);
    expect(result.current.totalPages).toBe(3);
  });

  it("reset restores initial state", () => {
    const { result } = renderHook(() =>
      useDataTable({ initialSortKey: "name", initialSortDir: "desc", totalItems: 100 }),
    );
    act(() => result.current.setPage(3));
    act(() => result.current.setSort("email"));
    act(() => result.current.reset());
    expect(result.current.page).toBe(1);
    expect(result.current.sortKey).toBe("name");
    expect(result.current.sortDir).toBe("desc");
  });
});
