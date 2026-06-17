import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ActionsPerDayChart } from "@/features/admin-auditoria-panel/components/ActionsPerDayChart";
import { CommsStatusChart } from "@/features/admin-auditoria-panel/components/CommsStatusChart";
import { InteractionsTable } from "@/features/admin-auditoria-panel/components/InteractionsTable";
import { LastActionsLog } from "@/features/admin-auditoria-panel/components/LastActionsLog";
import {
  useActionsPerDay,
  useCommsStatus,
  useInteractions,
  useLastActions,
} from "@/features/admin-auditoria-panel/hooks/useAuditoriaPanel";
import { renderHook } from "@testing-library/react";

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  };
}

const mockActions = [
  { fecha: "2025-06-01", accion: "login", total: 45 },
  { fecha: "2025-06-02", accion: "login", total: 52 },
];

const mockComms = [
  {
    usuario_id: "user-1",
    docente_email: "ana@test.com",
    pendientes: 12,
    enviadas: 45,
    fallidas: 2,
  },
];

const mockInteractions = [
  { usuario_id: "user-1", materia_id: "mat-1", accion: "consulta", total: 120 },
];

const mockLastActions = [
  {
    id: "act-1",
    fecha_hora: "2025-06-05T10:30:00Z",
    actor_id: "user-1",
    accion: "login",
    detalle: { message: "Inicio de sesión exitoso" },
  },
];

describe("ActionsPerDayChart", () => {
  it("renders loading state", () => {
    renderWithProviders(<ActionsPerDayChart isLoading={true} />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders empty state when no data", () => {
    renderWithProviders(<ActionsPerDayChart data={[]} isLoading={false} />);
    expect(screen.getByText("No hay datos disponibles")).toBeInTheDocument();
  });

  it("renders chart with data", () => {
    renderWithProviders(
      <ActionsPerDayChart data={mockActions} isLoading={false} />,
    );
    expect(screen.getByText("Acciones por Día")).toBeInTheDocument();
  });
});

describe("CommsStatusChart", () => {
  it("renders loading state", () => {
    renderWithProviders(<CommsStatusChart isLoading={true} />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders empty state when no data", () => {
    renderWithProviders(<CommsStatusChart data={[]} isLoading={false} />);
    expect(screen.getByText("No hay datos disponibles")).toBeInTheDocument();
  });

  it("renders chart with data", () => {
    renderWithProviders(
      <CommsStatusChart data={mockComms} isLoading={false} />,
    );
    expect(screen.getByText("Estado de Comunicaciones")).toBeInTheDocument();
  });
});

describe("InteractionsTable", () => {
  it("renders loading state", () => {
    renderWithProviders(<InteractionsTable isLoading={true} />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders empty state", () => {
    renderWithProviders(<InteractionsTable data={[]} isLoading={false} />);
    expect(screen.getByText("No hay interacciones registradas")).toBeInTheDocument();
  });

  it("renders interaction data", () => {
    renderWithProviders(
      <InteractionsTable data={mockInteractions} isLoading={false} />,
    );
    expect(screen.getByText("consulta")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
  });
});

describe("LastActionsLog", () => {
  it("renders loading state", () => {
    renderWithProviders(<LastActionsLog isLoading={true} />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders empty state", () => {
    renderWithProviders(<LastActionsLog data={[]} isLoading={false} />);
    expect(screen.getByText("No hay acciones recientes")).toBeInTheDocument();
  });

  it("renders last actions data", () => {
    renderWithProviders(
      <LastActionsLog data={mockLastActions} isLoading={false} />,
    );
    expect(screen.getByText("login")).toBeInTheDocument();
  });
});

describe("useActionsPerDay", () => {
  it("fetches actions per day data", async () => {
    const { result } = renderHook(() => useActionsPerDay(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});

describe("useCommsStatus", () => {
  it("fetches comms status data", async () => {
    const { result } = renderHook(() => useCommsStatus(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});

describe("useInteractions", () => {
  it("fetches interactions data", async () => {
    const { result } = renderHook(() => useInteractions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});

describe("useLastActions", () => {
  it("fetches last actions data", async () => {
    const { result } = renderHook(() => useLastActions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
    expect(Array.isArray(result.current.data)).toBe(true);
  });
});
