import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  getMisEquipos,
  asignacionMasiva,
  clonarEquipo,
  modificarVigencia,
  exportarEquipo,
} from "@/api/endpoints/equipos";

const BASE = "/api/v1";

describe("equipos API", () => {
  beforeEach(() => server.resetHandlers());

  it("getMisEquipos returns assignments list", async () => {
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
              comisiones: ["A", "B"],
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
    const res = await getMisEquipos({ solo_vigentes: true });
    expect(res.data.items).toHaveLength(1);
    expect(res.data.items[0].rol).toBe("PROFESOR");
  });

  it("asignacionMasiva creates bulk assignments", async () => {
    server.use(
      http.post(`${BASE}/equipos/asignacion-masiva`, () =>
        HttpResponse.json(
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
        ),
      ),
    );
    const res = await asignacionMasiva({
      usuario_ids: ["u1"],
      materia_id: "m1",
      cohorte_id: "c1",
      rol: "TUTOR",
    });
    expect(res.data).toHaveLength(1);
    expect(res.data[0].rol).toBe("TUTOR");
  });

  it("clonarEquipo duplicates assignments", async () => {
    server.use(
      http.post(`${BASE}/equipos/clonar`, () =>
        HttpResponse.json(
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
        ),
      ),
    );
    const res = await clonarEquipo({
      origen: { materia_id: "m1", carrera_id: null, cohorte_id: "c1" },
      destino: { materia_id: "m1", carrera_id: null, cohorte_id: "c2", desde: "2025-08-01T00:00:00", hasta: "2025-12-31T00:00:00" },
    });
    expect(res.data).toHaveLength(1);
    expect(res.data[0].cohorte_id).toBe("c2");
  });

  it("modificarVigencia updates dates in bulk", async () => {
    server.use(
      http.patch(`${BASE}/equipos/vigencia`, () =>
        HttpResponse.json({ filas_afectadas: 5 }),
      ),
    );
    const res = await modificarVigencia({
      materia_id: "m1",
      carrera_id: "carr1",
      cohorte_id: "c1",
      desde: "2025-03-01T00:00:00",
      hasta: "2025-12-31T00:00:00",
    });
    expect(res.data.filas_afectadas).toBe(5);
  });

  it("exportarEquipo downloads CSV", async () => {
    server.use(
      http.get(`${BASE}/equipos/exportar`, () =>
        HttpResponse.json(new Blob(["docente,rol,materia"], { type: "text/csv" })),
      ),
    );
    const res = await exportarEquipo({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data).toBeInstanceOf(Blob);
  });
});
