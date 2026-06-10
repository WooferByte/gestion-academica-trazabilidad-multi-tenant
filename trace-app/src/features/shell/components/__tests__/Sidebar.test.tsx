import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { Sidebar } from "@/features/shell/components/Sidebar";
import { createContext, useContext, type ReactNode } from "react";

const MockAuthContext = createContext<{
  isAuthenticated: boolean;
  isLoading: boolean;
  permissions: string[];
}>({
  isAuthenticated: false,
  isLoading: false,
  permissions: [],
});

function MockAuthProvider({
  children,
  value,
}: {
  children: ReactNode;
  value: { isAuthenticated: boolean; isLoading: boolean; permissions: string[] };
}) {
  return (
    <MockAuthContext.Provider value={value}>
      {children}
    </MockAuthContext.Provider>
  );
}

vi.mock("@/features/auth/hooks/useAuth", () => ({
  useAuth: () => {
    const ctx = useContext(MockAuthContext);
    return {
      ...ctx,
      user: {
        id: "user-1",
        email: "admin@test.com",
        nombre: "Admin",
        apellido: "Test",
        roles: ["ADMIN"],
        permisos: ctx.permissions,
        tenant_id: "tenant-1",
      },
      impersonating: false,
      login: vi.fn(),
      verify2fa: vi.fn(),
      logout: vi.fn(),
      requestRecovery: vi.fn(),
      confirmRecovery: vi.fn(),
    };
  },
}));

describe("Sidebar", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders items based on permissions", () => {
    renderWithProviders(
      <MockAuthProvider
        value={{
          isAuthenticated: true,
          isLoading: false,
          permissions: ["dashboard:ver", "estructura:gestionar", "atrasados:ver", "comunicacion:enviar"],
        }}
      >
        <Sidebar />
      </MockAuthProvider>,
      { initialEntries: ["/dashboard"] },
    );

    expect(screen.getByText("Panel General")).toBeInTheDocument();
    expect(screen.getByText("Académico")).toBeInTheDocument();
  });

  it("collapses and expands, persisting state", async () => {
    const userEventModule = await import("@testing-library/user-event");
    const user = userEventModule.default.setup();

    renderWithProviders(
      <MockAuthProvider
        value={{
          isAuthenticated: true,
          isLoading: false,
          permissions: ["dashboard:ver"],
        }}
      >
        <Sidebar />
      </MockAuthProvider>,
      { initialEntries: ["/dashboard"] },
    );

    // Initially expanded (sidebar renders with collapsed=false)
    const toggleBtn = screen.getByTitle("Colapsar menú");
    expect(toggleBtn).toBeInTheDocument();

    // Click to collapse
    await user.click(toggleBtn);
    expect(localStorage.getItem("trace_sidebar_collapsed")).toBe("true");

    // Click to expand
    const expandBtn = screen.getByTitle("Expandir menú");
    await user.click(expandBtn);
    expect(localStorage.getItem("trace_sidebar_collapsed")).toBe("false");
  });
});
