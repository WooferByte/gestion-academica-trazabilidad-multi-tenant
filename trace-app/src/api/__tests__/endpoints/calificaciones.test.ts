import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  importarConfirmar,
  listarCalificaciones,
} from "@/api/endpoints/calificaciones";

const BASE = "/api/v1";

describe("calificaciones API", () => {
  beforeEach(() => server.resetHandlers());

  it("importarConfirmar sends file_token and actividad_ids", async () => {
    server.use(
      http.post(`${BASE}/calificaciones/importar/confirmar`, () =>
        HttpResponse.json({ detail: "Importación exitosa", importados: 42 }),
      ),
    );

    const res = await importarConfirmar({ file_token: "t-1", actividad_ids: ["a1"] });
    expect(res.data.importados).toBe(42);
  });

  it("listarCalificaciones sends GET with params", async () => {
    server.use(
      http.get(`${BASE}/calificaciones`, () =>
        HttpResponse.json([{ id: "c1", alumno_id: "a1", actividad_id: "act1", nota: 8, fecha: "" }]),
      ),
    );

    const res = await listarCalificaciones({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data).toHaveLength(1);
    expect(res.data[0]?.nota).toBe(8);
  });
});
