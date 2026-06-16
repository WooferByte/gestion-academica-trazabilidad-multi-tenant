import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useAsignacionMasiva } from "@/features/equipos/hooks/useAsignacionMasiva";

const BASE = "/api/v1";

describe("useAsignacionMasiva", () => {
  beforeEach(() => server.resetHandlers());

  it("sends bulk assignment with correct payload", async () => {
    let capturedBody: unknown = null;

    server.use(
      http.post(`${BASE}/equipos/asignacion-masiva`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(
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
        );
      }),
    );

    const { result } = renderHook(() => useAsignacionMasiva(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      usuario_ids: ["u1", "u2"],
      materia_id: "m1",
      cohorte_id: "c1",
      rol: "TUTOR",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(capturedBody).toEqual({
      usuario_ids: ["u1", "u2"],
      materia_id: "m1",
      cohorte_id: "c1",
      rol: "TUTOR",
    });
  });
});
