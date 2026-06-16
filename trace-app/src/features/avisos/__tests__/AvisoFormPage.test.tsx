import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import AvisoFormPage from "@/features/avisos/pages/AvisoFormPage";

const BASE = "/api/v1";

describe("AvisoFormPage", () => {
  beforeEach(() => server.resetHandlers());

  it("shows conditional materia field when alcance is PorMateria", async () => {
    server.use(
      http.post(`${BASE}/avisos`, () =>
        HttpResponse.json(
          {
            id: "av1",
            tenant_id: "t1",
            alcance: "PorMateria",
            materia_id: "m1",
            cohorte_id: null,
            rol_destino: null,
            severidad: "Info",
            titulo: "Aviso Materia",
            cuerpo: "Cuerpo",
            inicio_vigencia: "2025-03-01T00:00:00",
            fin_vigencia: "2025-03-31T00:00:00",
            orden: 0,
            activo: true,
            requiere_ack: false,
            total_acks: 0,
            user_acked: false,
            created_at: "2025-03-01T00:00:00",
            updated_at: null,
          },
          { status: 201 },
        ),
      ),
    );

    renderWithProviders(<AvisoFormPage />, { initialEntries: ["/avisos/crear"] });

    const alcanceSelect = screen.getByLabelText(/alcance/i);
    fireEvent.change(alcanceSelect, { target: { value: "PorMateria" } });

    await waitFor(() => {
      expect(screen.getByLabelText(/materia/i)).toBeInTheDocument();
    });
  });

  it("shows conditional rol_destino field when alcance is PorRol", async () => {
    renderWithProviders(<AvisoFormPage />, { initialEntries: ["/avisos/crear"] });

    const alcanceSelect = screen.getByLabelText(/alcance/i);
    fireEvent.change(alcanceSelect, { target: { value: "PorRol" } });

    await waitFor(() => {
      expect(screen.getByLabelText(/rol destino/i)).toBeInTheDocument();
    });
  });
});
