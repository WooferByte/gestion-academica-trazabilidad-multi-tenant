import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useMisEquipos } from "@/features/equipos/hooks/useMisEquipos";

const BASE = "/api/v1";

describe("useMisEquipos", () => {
  beforeEach(() => server.resetHandlers());

  it("fetches mis equipos with correct query key", async () => {
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

    const { result } = renderHook(() => useMisEquipos({ solo_vigentes: true }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].rol).toBe("PROFESOR");
  });

  it("returns empty array when no data", async () => {
    server.use(
      http.get(`${BASE}/equipos/mis-equipos`, () =>
        HttpResponse.json({ items: [], total: 0 }),
      ),
    );

    const { result } = renderHook(() => useMisEquipos(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(0);
    expect(result.current.data?.total).toBe(0);
  });
});
