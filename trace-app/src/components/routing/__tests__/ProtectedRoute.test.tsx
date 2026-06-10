import { describe, it, expect, vi } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { ProtectedRoute } from "@/components/routing/ProtectedRoute";
import { Routes, Route } from "react-router-dom";
import { createContext, useContext, type ReactNode } from "react";
import type { User } from "@/features/auth/types/auth.types";

// Create a mock auth context
const MockAuthContext = createContext<{
  isAuthenticated: boolean;
  isLoading: boolean;
  permissions: string[];
  user: User | null;
}>({
  isAuthenticated: false,
  isLoading: false,
  permissions: [],
  user: null,
});

function MockAuthProvider({
  children,
  value,
}: {
  children: ReactNode;
  value: {
    isAuthenticated: boolean;
    isLoading: boolean;
    permissions: string[];
    user: User | null;
  };
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
      login: vi.fn(),
      verify2fa: vi.fn(),
      logout: vi.fn(),
      requestRecovery: vi.fn(),
      confirmRecovery: vi.fn(),
      impersonating: false,
    };
  },
}));

describe("ProtectedRoute", () => {
  it("redirects to /login when no session", () => {
    renderWithProviders(
      <MockAuthProvider
        value={{ isAuthenticated: false, isLoading: false, permissions: [], user: null }}
      >
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<p>Dashboard</p>} />
          </Route>
          <Route path="/login" element={<p>Login Page</p>} />
        </Routes>
      </MockAuthProvider>,
      { initialEntries: ["/dashboard"] },
    );

    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("shows 403 when permission is missing", () => {
    renderWithProviders(
      <MockAuthProvider
        value={{
          isAuthenticated: true,
          isLoading: false,
          permissions: [],
          user: {
            id: "user-1",
            email: "test@test.com",
            nombre: "Test",
            apellido: "User",
            roles: ["USER"],
            permisos: [],
            tenant_id: "tenant-1",
          },
        }}
      >
        <Routes>
          <Route element={<ProtectedRoute requiredPermission="admin:ver" />}>
            <Route path="/admin" element={<p>Admin Panel</p>} />
          </Route>
        </Routes>
      </MockAuthProvider>,
      { initialEntries: ["/admin"] },
    );

    expect(screen.getByText("403")).toBeInTheDocument();
    expect(screen.getByText("Sin permisos suficientes")).toBeInTheDocument();
  });
});
