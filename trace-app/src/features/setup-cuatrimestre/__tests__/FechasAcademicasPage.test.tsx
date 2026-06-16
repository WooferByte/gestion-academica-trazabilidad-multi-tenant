import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderWithProviders } from "@/test/test-utils";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import FechasAcademicasPage from "@/features/setup-cuatrimestre/pages/FechasAcademicasPage";

const BASE = "/api/v1";

describe("FechasAcademicasPage", () => {
  beforeEach(() => server.resetHandlers());

  it("renders and toggles between table and calendar view", async () => {
    server.use(
      http.get(`${BASE}/admin/fechas-academicas`, () =>
        HttpResponse.json({
          items: [
            {
              id: "f1",
              tenant_id: "t1",
              materia_id: "m1",
              cohorte_id: "co1",
              tipo: "parcial",
              numero: 1,
              periodo: "2026",
              fecha: "2026-08-15",
              titulo: "1er Parcial",
              created_at: "2026-06-01T00:00:00",
              updated_at: "2026-06-01T00:00:00",
              deleted_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    renderWithProviders(<FechasAcademicasPage />);

    await waitFor(() => {
      expect(screen.getByText("Fechas Académicas")).toBeInTheDocument();
    });

    const calendarButton = screen.getByText("Calendario");
    fireEvent.click(calendarButton);

    await waitFor(() => {
      expect(screen.getByText("1er Parcial")).toBeInTheDocument();
    });

    const tableButton = screen.getByText("Tabla");
    fireEvent.click(tableButton);

    await waitFor(() => {
      expect(screen.getByText("Fechas Académicas")).toBeInTheDocument();
    });
  });
});
