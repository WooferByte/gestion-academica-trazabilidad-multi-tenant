import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import MisTareasListPage from "@/features/tareas/pages/MisTareasListPage";

const BASE = "/api/v1";

describe("MisTareasListPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders tareas list with mock data", async () => {
    server.use(
      http.get(`${BASE}/tareas/mis-tareas`, () =>
        HttpResponse.json({
          items: [
            {
              id: "t1",
              tenant_id: "t1",
              materia_id: "m1",
              asignado_a: "u1",
              asignado_por: "u2",
              estado: "abierta",
              descripcion: "Corregir TP de Álgebra",
              contexto_id: null,
              comentarios: [],
              created_at: "2026-06-01T00:00:00",
              updated_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    renderWithProviders(<MisTareasListPage />);

    await waitFor(() => {
      expect(screen.getByText("Corregir TP de Álgebra")).toBeInTheDocument();
    });
  });
});
