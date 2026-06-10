import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { PublicRoute } from "@/components/routing/PublicRoute";
import { Routes, Route } from "react-router-dom";
import { createContext, useContext, type ReactNode } from "react";

const MockAuthContext = createContext<{
  isAuthenticated: boolean;
  isLoading: boolean;
}>({
  isAuthenticated: false,
  isLoading: false,
});

function MockAuthProvider({
  children,
  value,
}: {
  children: ReactNode;
  value: { isAuthenticated: boolean; isLoading: boolean };
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
      user: ctx.isAuthenticated
        ? {
            id: "user-1",
            email: "admin@test.com",
            nombre: "Admin",
            apellido: "Test",
            roles: ["ADMIN"],
            permisos: ["dashboard:ver"],
            tenant_id: "tenant-1",
          }
        : null,
      permissions: ctx.isAuthenticated ? ["dashboard:ver"] : [],
      impersonating: false,
      login: vi.fn(),
      verify2fa: vi.fn(),
      logout: vi.fn(),
      requestRecovery: vi.fn(),
      confirmRecovery: vi.fn(),
    };
  },
}));

describe("PublicRoute", () => {
  it("renders children when not authenticated", () => {
    renderWithProviders(
      <MockAuthProvider value={{ isAuthenticated: false, isLoading: false }}>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<p>Login Page</p>} />
          </Route>
          <Route path="/dashboard" element={<p>Dashboard</p>} />
        </Routes>
      </MockAuthProvider>,
      { initialEntries: ["/login"] },
    );

    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("redirects to /dashboard when authenticated", () => {
    renderWithProviders(
      <MockAuthProvider value={{ isAuthenticated: true, isLoading: false }}>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<p>Login Page</p>} />
          </Route>
          <Route path="/dashboard" element={<p>Dashboard</p>} />
        </Routes>
      </MockAuthProvider>,
      { initialEntries: ["/login"] },
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });
});
