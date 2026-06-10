import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import { createWrapper } from "@/test/test-utils";
import { useComisionSelector } from "@/features/academico/hooks/useComisionSelector";

const BASE = "/api/v1";

describe("useComisionSelector", () => {
  beforeEach(() => server.resetHandlers());

  it("should fetch comisiones and return materiasUnicas", async () => {
    server.use(
      http.get(`${BASE}/docente/comisiones`, () =>
        HttpResponse.json([
          { id: "c1", materia_id: "m1", materia_nombre: "Matemática", cohorte_id: "co1", cohorte_nombre: "2024A", rol: "profesor" },
          { id: "c2", materia_id: "m1", materia_nombre: "Matemática", cohorte_id: "co2", cohorte_nombre: "2024B", rol: "profesor" },
          { id: "c3", materia_id: "m2", materia_nombre: "Física", cohorte_id: "co1", cohorte_nombre: "2024A", rol: "tutor" },
        ]),
      ),
    );

    const { result } = renderHook(() => useComisionSelector(), {
      wrapper: createWrapper({ initialEntries: ["/academico"] }),
    });

    await waitFor(() => expect(result.current.query.isSuccess).toBe(true));

    expect(result.current.comisiones).toHaveLength(3);
    expect(result.current.materiasUnicas).toHaveLength(2);
    expect(result.current.materiasUnicas[0]?.materia_nombre).toBe("Matemática");

    const cohortes = result.current.getCohortes("m1");
    expect(cohortes).toHaveLength(2);
  });

  it("should handle empty comisiones", async () => {
    server.use(
      http.get(`${BASE}/docente/comisiones`, () => HttpResponse.json([])),
    );

    const { result } = renderHook(() => useComisionSelector(), {
      wrapper: createWrapper({ initialEntries: ["/academico"] }),
    });

    await waitFor(() => expect(result.current.query.isSuccess).toBe(true));

    expect(result.current.comisiones).toHaveLength(0);
    expect(result.current.materiasUnicas).toHaveLength(0);
  });

  it("should handle error", async () => {
    server.use(
      http.get(`${BASE}/docente/comisiones`, () => HttpResponse.json({ detail: "Error" }, { status: 500 })),
    );

    const { result } = renderHook(() => useComisionSelector(), {
      wrapper: createWrapper({ initialEntries: ["/academico"] }),
    });

    await waitFor(() => expect(result.current.query.isError).toBe(true));
  });
});
