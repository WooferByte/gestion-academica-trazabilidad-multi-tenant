import { type ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { render, type RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

interface WrapperOptions {
  initialEntries?: string[];
  authContext?: {
    user?: Record<string, unknown> | null;
    permissions?: string[];
    isAuthenticated?: boolean;
    isLoading?: boolean;
  };
}

export function createWrapper(options: WrapperOptions = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={options.initialEntries ?? ["/"]}>
          {children}
        </MemoryRouter>
      </QueryClientProvider>
    );
  };
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: WrapperOptions & Omit<RenderOptions, "wrapper">,
) {
  const { initialEntries, ...renderOptions } = options ?? {};
  return render(ui, {
    wrapper: createWrapper({ initialEntries }),
    ...renderOptions,
  });
}

export function createMockUser(overrides: Record<string, unknown> = {}) {
  return {
    id: "user-1",
    email: "admin@test.com",
    nombre: "Admin",
    apellido: "Test",
    roles: ["ADMIN"],
    permisos: [
      "dashboard:ver",
      "academico:ver",
      "materias:ver",
      "analisis:ver",
    ],
    tenant_id: "tenant-1",
    ...overrides,
  };
}
