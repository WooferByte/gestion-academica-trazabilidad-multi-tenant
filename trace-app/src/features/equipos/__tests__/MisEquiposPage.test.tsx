import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import MisEquiposPage from "@/features/equipos/pages/MisEquiposPage";

const BASE = "/api/v1";

describe("MisEquiposPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders table with mock data", async () => {
    server.use(
      http.get(`${BASE}/equipos/mis-equipos`, () =>
        HttpResponse.json({
          items: [
            {
              id: "a1",
              tenant_id: "t1",
              usuario_id: "u1",
              rol: "PROFESOR",
              materia_id: "m1",
              carrera_id: null,
              cohorte_id: "c1",
              comisiones: ["A"],
              responsable_id: null,
              desde: "2025-03-01T00:00:00",
              hasta: "2025-12-31T00:00:00",
              created_at: "2025-01-01T00:00:00",
              updated_at: "2025-01-01T00:00:00",
              deleted_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    renderWithProviders(<MisEquiposPage />);

    await waitFor(() => {
      expect(screen.getByText("PROFESOR")).toBeInTheDocument();
    });
  });
});
