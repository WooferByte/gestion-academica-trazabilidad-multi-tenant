import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useSlotsList, useCrearSlot } from "@/features/encuentros/hooks/useEncuentrosSlots";

const BASE = "/api/v1";

const mockSlots = {
  items: [
    {
      id: "slot-1",
      tenant_id: "t1",
      asignacion_id: "asig-1",
      materia_id: "mat-1",
      titulo: "Clase 1",
      hora: "18:00",
      dia_semana: "LUNES",
      fecha_inicio: "2026-03-01",
      cant_semanas: 8,
      fecha_unica: null,
      meet_url: null,
      vig_desde: null,
      vig_hasta: null,
      created_at: null,
      updated_at: null,
    },
  ],
  total: 1,
};

describe("useEncuentrosSlots", () => {
  beforeEach(() => server.resetHandlers());

  it("returns list of slots", async () => {
    server.use(
      http.get(`${BASE}/encuentros/slots`, () => HttpResponse.json(mockSlots)),
    );

    const { result } = renderHook(() => useSlotsList("mat-1"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].titulo).toBe("Clase 1");
  });

  it("creates a slot successfully", async () => {
    server.use(
      http.post(`${BASE}/encuentros/slots`, () =>
        HttpResponse.json(mockSlots.items[0], { status: 201 }),
      ),
    );

    const { result } = renderHook(() => useCrearSlot(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      asignacion_id: "asig-1",
      materia_id: "mat-1",
      titulo: "Clase 1",
      hora: "18:00",
      dia_semana: "LUNES",
      fecha_inicio: "2026-03-01",
      cant_semanas: 8,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.titulo).toBe("Clase 1");
  });
});
