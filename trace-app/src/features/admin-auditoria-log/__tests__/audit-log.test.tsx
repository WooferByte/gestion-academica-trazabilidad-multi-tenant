import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook } from "@testing-library/react";
import { useAuditLog } from "@/features/admin-auditoria-log/hooks/useAuditLog";
import AdminAuditoriaLogPage from "@/features/admin-auditoria-log/pages/AdminAuditoriaLogPage";

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  };
}

describe("useAuditLog", () => {
  it("fetches audit log with default filters", async () => {
    const { result } = renderHook(
      () => useAuditLog({ page: 1, page_size: 25 }),
      { wrapper: createWrapper() },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(result.current.data!.items).toBeDefined();
    expect(Array.isArray(result.current.data!.items)).toBe(true);
    expect(result.current.data!.total).toBeGreaterThan(0);
    expect(result.current.data!.page).toBe(1);
  });

  it("fetches audit log with filters", async () => {
    const { result } = renderHook(
      () => useAuditLog({ page: 1, page_size: 10, desde: "2025-01-01", hasta: "2025-12-31" }),
      { wrapper: createWrapper() },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(result.current.data!.page_size).toBe(10);
  });
});

describe("AdminAuditoriaLogPage", () => {
  it("renders page header", () => {
    renderWithProviders(<AdminAuditoriaLogPage />);
    expect(screen.getByText("Registro de Auditoría")).toBeInTheDocument();
  });

  it("renders filter bar", () => {
    renderWithProviders(<AdminAuditoriaLogPage />);
    expect(screen.getByText("Desde")).toBeInTheDocument();
    expect(screen.getByText("Hasta")).toBeInTheDocument();
    expect(screen.getByText("Materia ID")).toBeInTheDocument();
    expect(screen.getByText("Usuario ID")).toBeInTheDocument();
  });

  it("renders audit log data in table", async () => {
    renderWithProviders(<AdminAuditoriaLogPage />);

    await waitFor(() => {
      expect(screen.getByText("192.168.1.1")).toBeInTheDocument();
    });
  });

  it("renders column headers", async () => {
    renderWithProviders(<AdminAuditoriaLogPage />);

    await waitFor(() => {
      expect(screen.getByText("IP Origen")).toBeInTheDocument();
    });
    expect(screen.getByText("Acción")).toBeInTheDocument();
  });
});
