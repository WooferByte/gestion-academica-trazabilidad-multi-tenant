import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useClonarEquipo } from "@/features/equipos/hooks/useClonarEquipo";

const BASE = "/api/v1";

describe("useClonarEquipo", () => {
  beforeEach(() => server.resetHandlers());

  it("sends clone request with origen/destino structure", async () => {
    let capturedBody: unknown = null;

    server.use(
      http.post(`${BASE}/equipos/clonar`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(
          [
            {
              id: "a2",
              tenant_id: "t1",
              usuario_id: "u1",
              rol: "PROFESOR",
              materia_id: "m1",
              carrera_id: null,
              cohorte_id: "c2",
              comisiones: null,
              responsable_id: null,
              desde: "2025-08-01T00:00:00",
              hasta: "2025-12-31T00:00:00",
              created_at: "2025-06-01T00:00:00",
              updated_at: "2025-06-01T00:00:00",
              deleted_at: null,
            },
          ],
          { status: 201 },
        );
      }),
    );

    const { result } = renderHook(() => useClonarEquipo(), {
      wrapper: createWrapper(),
    });

    const payload = {
      origen: { materia_id: "m1", carrera_id: null, cohorte_id: "c1" },
      destino: {
        materia_id: "m1",
        carrera_id: null,
        cohorte_id: "c2",
        desde: "2025-08-01T00:00:00",
        hasta: "2025-12-31T00:00:00",
      },
    };

    result.current.mutate(payload);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(capturedBody).toEqual(payload);
  });
});
