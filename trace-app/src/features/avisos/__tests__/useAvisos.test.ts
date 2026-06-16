import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { renderHook, waitFor } from "@testing-library/react";
import { createWrapper } from "@/test/test-utils";
import { useAvisos } from "@/features/avisos/hooks/useAvisos";

const BASE = "/api/v1";

const mockAvisos = {
  items: [
    {
      id: "av1",
      tenant_id: "t1",
      alcance: "Global",
      materia_id: null,
      cohorte_id: null,
      rol_destino: null,
      severidad: "Info",
      titulo: "Aviso Global",
      cuerpo: "Cuerpo",
      inicio_vigencia: "2025-03-01T00:00:00",
      fin_vigencia: "2025-03-31T00:00:00",
      orden: 0,
      activo: true,
      requiere_ack: false,
      total_acks: 0,
      user_acked: false,
      created_at: "2025-03-01T00:00:00",
      updated_at: null,
    },
    {
      id: "av2",
      tenant_id: "t1",
      alcance: "PorRol",
      materia_id: null,
      cohorte_id: null,
      rol_destino: "PROFESOR",
      severidad: "Urgente",
      titulo: "Aviso Urgente",
      cuerpo: "Cuerpo urgente",
      inicio_vigencia: "2025-03-01T00:00:00",
      fin_vigencia: "2025-03-31T00:00:00",
      orden: 1,
      activo: true,
      requiere_ack: true,
      total_acks: 0,
      user_acked: false,
      created_at: "2025-03-01T00:00:00",
      updated_at: null,
    },
  ],
  total: 2,
};

describe("useAvisos", () => {
  beforeEach(() => server.resetHandlers());

  it("returns list of avisos", async () => {
    server.use(
      http.get(`${BASE}/avisos`, () => HttpResponse.json(mockAvisos)),
    );

    const { result } = renderHook(() => useAvisos(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(2);
  });

  it("filters by alcance", async () => {
    server.use(
      http.get(`${BASE}/avisos`, () => HttpResponse.json(mockAvisos)),
    );

    const { result } = renderHook(() => useAvisos({ alcance: "PorRol" }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(result.current.data?.items[0].alcance).toBe("PorRol");
  });
});
