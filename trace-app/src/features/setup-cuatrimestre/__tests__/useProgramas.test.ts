import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useProgramasList, useCrearPrograma } from "@/features/setup-cuatrimestre/hooks/useProgramas";

const BASE = "/api/v1";

describe("useProgramas", () => {
  beforeEach(() => server.resetHandlers());

  it("fetches programas list", async () => {
    server.use(
      http.get(`${BASE}/admin/programas`, () =>
        HttpResponse.json({
          items: [
            {
              id: "p1",
              tenant_id: "t1",
              materia_id: "m1",
              carrera_id: "c1",
              cohorte_id: "co1",
              titulo: "Programa de Álgebra 2026",
              referencia_archivo: null,
              cargado_at: null,
              created_at: "2026-01-15T00:00:00",
              updated_at: "2026-01-15T00:00:00",
              deleted_at: null,
            },
          ],
          total: 1,
        }),
      ),
    );

    const { result } = renderHook(() => useProgramasList(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
  });

  it("creates a programa", async () => {
    server.use(
      http.post(`${BASE}/admin/programas`, () =>
        HttpResponse.json({
          id: "p2",
          tenant_id: "t1",
          materia_id: "m2",
          carrera_id: "c1",
          cohorte_id: "co1",
          titulo: "Programa de Análisis",
          referencia_archivo: null,
          cargado_at: null,
          created_at: "2026-06-01T00:00:00",
          updated_at: "2026-06-01T00:00:00",
          deleted_at: null,
        }),
      ),
    );

    const { result } = renderHook(() => useCrearPrograma(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      materia_id: "m2",
      carrera_id: "c1",
      cohorte_id: "co1",
      titulo: "Programa de Análisis",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.titulo).toBe("Programa de Análisis");
  });
});
