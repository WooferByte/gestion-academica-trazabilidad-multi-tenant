import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useFechasList, useCrearFecha } from "@/features/setup-cuatrimestre/hooks/useFechasAcademicas";

const BASE = "/api/v1";

describe("useFechasAcademicas", () => {
  beforeEach(() => server.resetHandlers());

  it("fetches fechas academicas list", async () => {
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

    const { result } = renderHook(() => useFechasList(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].tipo).toBe("parcial");
  });

  it("creates a fecha academica", async () => {
    server.use(
      http.post(`${BASE}/admin/fechas-academicas`, () =>
        HttpResponse.json({
          id: "f2",
          tenant_id: "t1",
          materia_id: "m1",
          cohorte_id: "co1",
          tipo: "tp",
          numero: 1,
          periodo: "2026",
          fecha: "2026-09-01",
          titulo: "TP 1",
          created_at: "2026-06-02T00:00:00",
          updated_at: "2026-06-02T00:00:00",
          deleted_at: null,
        }),
      ),
    );

    const { result } = renderHook(() => useCrearFecha(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      materia_id: "m1",
      cohorte_id: "co1",
      tipo: "tp",
      numero: 1,
      periodo: "2026",
      fecha: "2026-09-01",
      titulo: "TP 1",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.tipo).toBe("tp");
    expect(result.current.data?.titulo).toBe("TP 1");
  });
});
