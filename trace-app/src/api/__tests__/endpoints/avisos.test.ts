import { describe, it, expect, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "@/test/mocks/server";
import {
  crearAviso,
  listarAvisos,
  obtenerAviso,
  actualizarAviso,
  eliminarAviso,
  confirmarLectura,
} from "@/api/endpoints/avisos";

const BASE = "/api/v1";

describe("avisos API", () => {
  beforeEach(() => server.resetHandlers());

  it("crearAviso creates and returns aviso", async () => {
    server.use(
      http.post(`${BASE}/avisos`, () =>
        HttpResponse.json(
          {
            id: "av1",
            tenant_id: "t1",
            alcance: "Global",
            materia_id: null,
            cohorte_id: null,
            rol_destino: null,
            severidad: "Info",
            titulo: "Bienvenidos",
            cuerpo: "Inicio de cuatrimestre",
            inicio_vigencia: "2025-03-01T00:00:00",
            fin_vigencia: "2025-03-31T00:00:00",
            orden: 0,
            activo: true,
            requiere_ack: true,
            total_acks: 0,
            user_acked: false,
            created_at: "2025-03-01T00:00:00",
            updated_at: null,
          },
          { status: 201 },
        ),
      ),
    );
    const res = await crearAviso({
      alcance: "Global",
      titulo: "Bienvenidos",
      cuerpo: "Inicio de cuatrimestre",
      inicio_vigencia: "2025-03-01T00:00:00",
      fin_vigencia: "2025-03-31T00:00:00",
      requiere_ack: true,
    });
    expect(res.data.titulo).toBe("Bienvenidos");
    expect(res.data.activo).toBe(true);
  });

  it("listarAvisos returns avisos list", async () => {
    server.use(
      http.get(`${BASE}/avisos`, () =>
        HttpResponse.json({
          items: [
            {
              id: "av1",
              tenant_id: "t1",
              alcance: "Global",
              materia_id: null,
              cohorte_id: null,
              rol_destino: null,
              severidad: "Info",
              titulo: "Aviso 1",
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
          ],
          total: 1,
        }),
      ),
    );
    const res = await listarAvisos();
    expect(res.data.items).toHaveLength(1);
  });

  it("obtenerAviso returns single aviso", async () => {
    server.use(
      http.get(`${BASE}/avisos/av1`, () =>
        HttpResponse.json({
          id: "av1",
          tenant_id: "t1",
          alcance: "Global",
          materia_id: null,
          cohorte_id: null,
          rol_destino: null,
          severidad: "Info",
          titulo: "Aviso 1",
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
        }),
      ),
    );
    const res = await obtenerAviso("av1");
    expect(res.data.id).toBe("av1");
  });

  it("actualizarAviso updates aviso", async () => {
    server.use(
      http.patch(`${BASE}/avisos/av1`, () =>
        HttpResponse.json({
          id: "av1",
          tenant_id: "t1",
          alcance: "Global",
          materia_id: null,
          cohorte_id: null,
          rol_destino: null,
          severidad: "Urgente",
          titulo: "Aviso actualizado",
          cuerpo: "Cuerpo actualizado",
          inicio_vigencia: "2025-03-01T00:00:00",
          fin_vigencia: "2025-03-31T00:00:00",
          orden: 0,
          activo: true,
          requiere_ack: false,
          total_acks: 0,
          user_acked: false,
          created_at: "2025-03-01T00:00:00",
          updated_at: "2025-03-02T00:00:00",
        }),
      ),
    );
    const res = await actualizarAviso("av1", { titulo: "Aviso actualizado", severidad: "Urgente" });
    expect(res.data.titulo).toBe("Aviso actualizado");
    expect(res.data.severidad).toBe("Urgente");
  });

  it("eliminarAviso deactivates aviso", async () => {
    server.use(
      http.delete(`${BASE}/avisos/av1`, () =>
        HttpResponse.json({ detail: "Aviso desactivado" }),
      ),
    );
    const res = await eliminarAviso("av1");
    expect(res.data.detail).toBe("Aviso desactivado");
  });

  it("confirmarLectura acknowledges aviso", async () => {
    server.use(
      http.post(`${BASE}/avisos/av1/ack`, () =>
        HttpResponse.json(
          {
            id: "ack-1",
            aviso_id: "av1",
            usuario_id: "u1",
            confirmado_at: "2025-03-01T12:00:00",
          },
          { status: 201 },
        ),
      ),
    );
    const res = await confirmarLectura("av1");
    expect(res.data.aviso_id).toBe("av1");
    expect(res.data.usuario_id).toBe("u1");
  });
});
