import { describe, it, expect, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { getUsuarios } from "../services/usuarios.service";
import AdminUsuariosPage from "../pages/AdminUsuariosPage";
import { UsuarioFormModal } from "../components/UsuarioFormModal";

describe("Usuarios Service", () => {
  it("getUsuarios returns list without PII fields", async () => {
    const res = await getUsuarios();
    expect(res.status).toBe(200);
    expect(Array.isArray(res.data.items)).toBe(true);
    for (const usuario of res.data.items) {
      expect(usuario).toHaveProperty("id");
      expect(usuario).toHaveProperty("nombre");
      expect(usuario).not.toHaveProperty("dni");
      expect(usuario).not.toHaveProperty("cuil");
      expect(usuario).not.toHaveProperty("cbu");
    }
  });

  it("getUsuarios filters by activo", async () => {
    const res = await getUsuarios({ activo: true });
    expect(res.data.items.every((u) => u.is_active === true || u.estado === "Activo")).toBe(true);
  });

  it("createUsuario sends POST without PII leakage in response", async () => {
    const res = await import("../services/usuarios.service").then((m) =>
      m.createUsuario({
        nombre: "Test",
        apellido: "User",
        email: "test@test.com",
        dni: "12345678",
        cuil: "20-12345678-9",
        cbu: "1234567890123456789012",
      }),
    );
    expect(res.status).toBe(201);
    expect(res.data.nombre).toBe("Test");
    expect(res.data).not.toHaveProperty("dni");
    expect(res.data).not.toHaveProperty("cuil");
    expect(res.data).not.toHaveProperty("cbu");
  });
});

describe("PII Not Exposed in GET", () => {
  it("GET /admin/usuarios response does not contain sensitive PII keys", async () => {
    const res = await getUsuarios();
    for (const usuario of res.data.items) {
      const keys = Object.keys(usuario);
      expect(keys).not.toContain("dni");
      expect(keys).not.toContain("cuil");
      expect(keys).not.toContain("cbu");
      expect(keys).not.toContain("alias_cbu");
    }
  });
});

describe("UsuarioFormModal", () => {
  const defaultProps = {
    open: true,
    onClose: vi.fn(),
    usuario: null,
  };

  it("renders create mode with empty fields", () => {
    renderWithProviders(<UsuarioFormModal {...defaultProps} />);
    expect(screen.getByText("Nuevo usuario")).toBeInTheDocument();
    expect(screen.getByLabelText("DNI")).toHaveValue("");
  });

  it("renders edit mode with PII fields showing dato cifrado placeholder", () => {
    renderWithProviders(
      <UsuarioFormModal
        {...defaultProps}
        usuario={{
          id: "user-1",
          nombre: "Admin",
          apellidos: "Test",
          email: "admin@test.com",
          legajo: "LEG-001",
          banco: "Banco Nación",
          regional: "Córdoba",
          facturador: true,
          roles: ["ADMIN"],
          activo: true,
        }}
      />,
    );
    expect(screen.getByText("Editar usuario")).toBeInTheDocument();
    const dniInput = screen.getByLabelText("DNI");
    expect(dniInput).toHaveAttribute("placeholder", "Dato cifrado");
    expect(dniInput).toHaveValue("");
  });

  it("shows validation errors for required fields", async () => {
    renderWithProviders(<UsuarioFormModal {...defaultProps} />);
    screen.getByText("Crear").click();
    await waitFor(() => {
      expect(screen.getByText("El nombre es requerido")).toBeInTheDocument();
      expect(screen.getByText("Email inválido")).toBeInTheDocument();
    });
  });
});

describe("AdminUsuariosPage", () => {
  it("renders page header", () => {
    renderWithProviders(<AdminUsuariosPage />);
    expect(screen.getByText("Usuarios")).toBeInTheDocument();
    expect(screen.getByText("Nuevo usuario")).toBeInTheDocument();
  });

  it("renders filter bar with estado filter", () => {
    renderWithProviders(<AdminUsuariosPage />);
    expect(screen.getByText("Estado")).toBeInTheDocument();
  });

  it("renders table headers", async () => {
    renderWithProviders(<AdminUsuariosPage />);
    await waitFor(() => {
      expect(screen.getByText("Nombre")).toBeInTheDocument();
    });
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Rol")).toBeInTheDocument();
  });
});
