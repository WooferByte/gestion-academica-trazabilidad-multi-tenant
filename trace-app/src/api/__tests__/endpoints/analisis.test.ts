import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  getAtrasados,
  getRanking,
  getNotasFinales,
  getTpsSinCorregir,
  getReportesRapidos,
  getMonitorSeguimiento,
  getMonitorGeneral,
} from "@/api/endpoints/analisis";

const BASE = "/api/v1";

describe("analisis API", () => {
  beforeEach(() => server.resetHandlers());

  it("getAtrasados returns students", async () => {
    server.use(
      http.get(`${BASE}/analisis/atrasados`, () =>
        HttpResponse.json({ alumnos: [{ id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", actividades_totales: 5, actividades_aprobadas: 2, estado: "faltantes" }] }),
      ),
    );
    const res = await getAtrasados({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.alumnos).toHaveLength(1);
  });

  it("getRanking returns sorted list", async () => {
    server.use(
      http.get(`${BASE}/analisis/ranking`, () =>
        HttpResponse.json({ alumnos: [{ id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", actividades_aprobadas: 8, actividades_totales: 10, porcentaje: 80 }] }),
      ),
    );
    const res = await getRanking({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.alumnos?.[0]?.porcentaje).toBe(80);
  });

  it("getNotasFinales returns grade matrix", async () => {
    server.use(
      http.get(`${BASE}/analisis/notas-finales`, () =>
        HttpResponse.json({ actividades: [{ id: "act1", nombre: "TP1", tipo: "tp", fecha: "" }], alumnos: [{ alumno_id: "a1", nombre: "Juan", apellido: "Pérez", legajo: "L001", notas: { act1: 8 } }] }),
      ),
    );
    const res = await getNotasFinales({ materia_id: "m1", cohorte_id: "c1", actividades: "act1" });
    expect(res.data.actividades).toHaveLength(1);
  });

  it("getTpsSinCorregir returns pending TPs", async () => {
    server.use(
      http.get(`${BASE}/analisis/tps-sin-corregir`, () =>
        HttpResponse.json({ items: [{ entrada_padron_id: "a1", nombre: "Juan", apellido: "Pérez", actividad: "TP1", comision: "A" }], total: 1 }),
      ),
    );
    const res = await getTpsSinCorregir({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.items).toHaveLength(1);
  });

  it("getReportesRapidos returns KPIs", async () => {
    server.use(
      http.get(`${BASE}/analisis/reportes-rapidos`, () =>
        HttpResponse.json({ materia_id: "m1", cohorte_id: "c1", kpis: { total_alumnos: 30, total_actividades: 5, aprobados: 20, atrasados: 10, promedio_general: 65 } }),
      ),
    );
    const res = await getReportesRapidos({ materia_id: "m1", cohorte_id: "c1" });
    expect(res.data.kpis.total_alumnos).toBe(30);
  });

  it("getMonitorSeguimiento returns items", async () => {
    server.use(
      http.get(`${BASE}/analisis/monitor-seguimiento`, () =>
        HttpResponse.json({ items: [{ entrada_padron_id: "a1", nombre: "Juan", apellidos: "Pérez", comision: "A", materia_id: "m1", actividad: "TP1", nota_numerica: 85, nota_textual: null, aprobado: true, importado_at: "2024-01-01T00:00:00Z" }], total: 1 }),
      ),
    );
    const res = await getMonitorSeguimiento();
    expect(res.data.items).toHaveLength(1);
  });

  it("getMonitorGeneral returns aggregated data", async () => {
    server.use(
      http.get(`${BASE}/analisis/monitor-general`, () =>
        HttpResponse.json({ items: [{ entrada_padron_id: "a1", nombre: "Juan", apellidos: "Pérez", comision: "A", regional: "CABA", materia_id: "m1", materia_nombre: "Matemática", actividad: "TP1", nota_numerica: 85, nota_textual: null, aprobado: true, importado_at: "2024-01-01T00:00:00Z" }], total: 1 }),
      ),
    );
    const res = await getMonitorGeneral();
    expect(res.data.items).toHaveLength(1);
  });
});
