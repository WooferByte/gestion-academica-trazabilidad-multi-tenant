import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import AsignacionMasivaPage from "@/features/equipos/pages/AsignacionMasivaPage";

const BASE = "/api/v1";

describe("AsignacionMasivaPage", () => {
  beforeEach(() => server.resetHandlers());

  it("shows validation error when submitting without docentes", async () => {
    renderWithProviders(<AsignacionMasivaPage />);

    const submitButton = screen.getByRole("button", { name: /asignar/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Seleccioná al menos un docente")).toBeInTheDocument();
    });
  });

  it("submits successfully with docentes selected", async () => {
    server.use(
      http.post(`${BASE}/equipos/asignacion-masiva`, () =>
        HttpResponse.json(
          [
            {
              id: "a1",
              tenant_id: "t1",
              usuario_id: "u1",
              rol: "TUTOR",
              materia_id: "m1",
              carrera_id: null,
              cohorte_id: "c1",
              comisiones: null,
              responsable_id: null,
              desde: "2025-03-01T00:00:00",
              hasta: "2025-12-31T00:00:00",
              created_at: "2025-01-01T00:00:00",
              updated_at: "2025-01-01T00:00:00",
              deleted_at: null,
            },
          ],
          { status: 201 },
        ),
      ),
    );

    renderWithProviders(<AsignacionMasivaPage />);

    const docenteInput = screen.getByPlaceholderText("ID del docente");
    const addButton = screen.getByRole("button", { name: /agregar/i });

    fireEvent.change(docenteInput, { target: { value: "u1" } });
    fireEvent.click(addButton);

    const rolSelect = screen.getByRole("combobox");
    fireEvent.change(rolSelect, { target: { value: "TUTOR" } });

    const submitButton = screen.getByRole("button", { name: /asignar/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByText("Seleccioná al menos un docente")).not.toBeInTheDocument();
    });
  });
});
