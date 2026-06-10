import csv
import io
import uuid
from datetime import datetime

from app.repositories.analisis_repository import AnalisisRepository
from app.repositories.umbral_repository import UmbralMateriaRepository
from app.schemas.analisis import (
    AlumnoAtrasado,
    MonitorEntry,
    MonitorSeguimiento,
    NotaFinal,
    RankingEntry,
    ReporteRapido,
    TPSinCorregir,
)
from app.schemas.calificaciones import VALIDOS_TEXTUALES_APROBATORIOS


def _es_aprobado(
    nota_numerica: float | None,
    nota_textual: str | None,
    umbral_pct: int,
    valores_aprobatorios: set[str] | None,
) -> bool | None:
    if nota_numerica is not None:
        return float(nota_numerica) >= umbral_pct
    if nota_textual:
        aprobatorios = valores_aprobatorios or VALIDOS_TEXTUALES_APROBATORIOS
        return nota_textual in aprobatorios
    return None


class AnalisisService:
    def __init__(self, session, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._analisis_repo = AnalisisRepository(session, tenant_id)
        self._umbral_repo = UmbralMateriaRepository(session, tenant_id)

    async def _get_umbral(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> tuple[int, set[str] | None]:
        umbral = await self._umbral_repo.get_by_materia_cohorte(materia_id, cohorte_id)
        if umbral:
            vals = set(umbral.valores_aprobatorios) if umbral.valores_aprobatorios else None
            return umbral.umbral_pct, vals
        return 60, None

    async def calcular_atrasados(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[AlumnoAtrasado]:
        calificaciones = await self._analisis_repo.get_calificaciones_con_alumnos(
            materia_id, cohorte_id,
        )
        actividades = await self._analisis_repo.get_actividades_por_materia(
            materia_id, cohorte_id,
        )
        alumnos = await self._analisis_repo.get_alumnos_por_materia(
            materia_id, cohorte_id,
        )
        umbral_pct, valores_aprobatorios = await self._get_umbral(materia_id, cohorte_id)

        alumno_actividades: dict[uuid.UUID, dict[str, dict]] = {}
        for c in calificaciones:
            ep_id = c['entrada_padron_id']
            if ep_id not in alumno_actividades:
                alumno_actividades[ep_id] = {}
            alumno_actividades[ep_id][c['actividad']] = c

        result = []
        for alumno in alumnos:
            ep_id = alumno.id
            acts = alumno_actividades.get(ep_id, {})
            faltantes = [a for a in actividades if a not in acts]
            desaprobadas = []
            aprobadas = 0
            for act_name, calif in acts.items():
                aprobado = _es_aprobado(
                    float(calif['nota_numerica']) if calif.get('nota_numerica') is not None else None,
                    calif.get('nota_textual'),
                    umbral_pct,
                    valores_aprobatorios,
                )
                if aprobado is True:
                    aprobadas += 1
                elif aprobado is False:
                    desaprobadas.append(act_name)

            if faltantes or desaprobadas:
                result.append(AlumnoAtrasado(
                    entrada_padron_id=ep_id,
                    nombre=alumno.nombre,
                    apellidos=alumno.apellidos,
                    email=alumno.email,
                    comision=alumno.comision,
                    regional=alumno.regional,
                    actividades_faltantes=faltantes,
                    actividades_desaprobadas=desaprobadas,
                    total_actividades=len(actividades),
                    aprobadas=aprobadas,
                ))

        return result

    async def calcular_ranking(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[RankingEntry]:
        calificaciones = await self._analisis_repo.get_calificaciones_con_alumnos(
            materia_id, cohorte_id,
        )
        umbral_pct, valores_aprobatorios = await self._get_umbral(materia_id, cohorte_id)

        alumno_aprobadas: dict[uuid.UUID, dict] = {}
        for c in calificaciones:
            ep_id = c['entrada_padron_id']
            if ep_id not in alumno_aprobadas:
                alumno_aprobadas[ep_id] = {
                    'nombre': c['nombre'],
                    'apellidos': c['apellidos'],
                    'comision': c['comision'],
                    'aprobadas': 0,
                }
            aprobado = _es_aprobado(
                float(c['nota_numerica']) if c.get('nota_numerica') is not None else None,
                c.get('nota_textual'),
                umbral_pct,
                valores_aprobatorios,
            )
            if aprobado is True:
                alumno_aprobadas[ep_id]['aprobadas'] += 1

        entries = [
            RankingEntry(
                entrada_padron_id=ep_id,
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                comision=data['comision'],
                actividades_aprobadas=data['aprobadas'],
            )
            for ep_id, data in alumno_aprobadas.items()
            if data['aprobadas'] >= 1
        ]

        entries.sort(key=lambda e: (-e.actividades_aprobadas, e.apellidos, e.nombre))
        return entries

    async def listar_actividades(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[dict]:
        actividades = await self._analisis_repo.get_actividades_por_materia(
            materia_id, cohorte_id,
        )
        return [{'nombre': a, 'id': a} for a in actividades]

    async def calcular_reporte_rapido(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> ReporteRapido:
        calificaciones = await self._analisis_repo.get_calificaciones_con_alumnos(
            materia_id, cohorte_id,
        )
        actividades = await self._analisis_repo.get_actividades_por_materia(
            materia_id, cohorte_id,
        )
        alumnos = await self._analisis_repo.get_alumnos_por_materia(
            materia_id, cohorte_id,
        )
        umbral_pct, valores_aprobatorios = await self._get_umbral(materia_id, cohorte_id)

        alumno_aprobado: dict[uuid.UUID, bool] = {}
        total_notas = 0.0
        total_notas_count = 0

        for c in calificaciones:
            ep_id = c['entrada_padron_id']
            aprobado = _es_aprobado(
                float(c['nota_numerica']) if c.get('nota_numerica') is not None else None,
                c.get('nota_textual'),
                umbral_pct,
                valores_aprobatorios,
            )
            if aprobado is True:
                alumno_aprobado[ep_id] = True
            elif aprobado is False and ep_id not in alumno_aprobado:
                alumno_aprobado[ep_id] = False
            if c.get('nota_numerica') is not None:
                total_notas += float(c['nota_numerica'])
                total_notas_count += 1

        alumnos_aprobados = sum(1 for v in alumno_aprobado.values() if v)
        alumnos_atrasados = len(alumnos) - alumnos_aprobados
        promedio = round(total_notas / total_notas_count, 2) if total_notas_count > 0 else None

        return ReporteRapido(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            total_alumnos=len(alumnos),
            total_actividades=len(actividades),
            alumnos_aprobados=alumnos_aprobados,
            alumnos_atrasados=alumnos_atrasados,
            promedio_general=promedio,
        )

    async def calcular_notas_finales(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID, actividades: list[str],
    ) -> list[NotaFinal]:
        calificaciones = await self._analisis_repo.get_calificaciones_con_alumnos(
            materia_id, cohorte_id,
        )
        actividades_set = set(actividades)

        alumno_notas: dict[uuid.UUID, dict] = {}
        for c in calificaciones:
            if c['actividad'] not in actividades_set:
                continue
            ep_id = c['entrada_padron_id']
            if ep_id not in alumno_notas:
                alumno_notas[ep_id] = {
                    'nombre': c['nombre'],
                    'apellidos': c['apellidos'],
                    'notas': [],
                }
            if c.get('nota_numerica') is not None:
                alumno_notas[ep_id]['notas'].append(float(c['nota_numerica']))

        result = []
        for ep_id, data in alumno_notas.items():
            notas = data['notas']
            if notas:
                nota_final = round(sum(notas) / len(notas), 2)
            else:
                nota_final = None
            result.append(NotaFinal(
                entrada_padron_id=ep_id,
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                nota_final=nota_final,
                actividades_consideradas=len(notas),
            ))

        return result

    async def exportar_tps_sin_corregir(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[TPSinCorregir]:
        calificaciones = await self._analisis_repo.get_calificaciones_con_alumnos(
            materia_id, cohorte_id,
        )
        actividades = await self._analisis_repo.get_actividades_por_materia(
            materia_id, cohorte_id,
        )
        alumnos = await self._analisis_repo.get_alumnos_por_materia(
            materia_id, cohorte_id,
        )

        alumno_calificadas: dict[uuid.UUID, set[str]] = {}
        for c in calificaciones:
            ep_id = c['entrada_padron_id']
            if ep_id not in alumno_calificadas:
                alumno_calificadas[ep_id] = set()
            alumno_calificadas[ep_id].add(c['actividad'])

        result = []
        for alumno in alumnos:
            calificadas = alumno_calificadas.get(alumno.id, set())
            for actividad in actividades:
                if actividad not in calificadas:
                    result.append(TPSinCorregir(
                        alumno_nombre=alumno.nombre,
                        alumno_apellidos=alumno.apellidos,
                        actividad=actividad,
                        comision=alumno.comision,
                    ))

        return result

    async def monitor_general(
        self,
        materia_id: uuid.UUID | None = None,
        comision: str | None = None,
        regional: str | None = None,
        busqueda: str | None = None,
    ) -> list[MonitorEntry]:
        calificaciones = await self._analisis_repo.get_calificaciones_por_tenant(
            materia_id=materia_id,
            comision=comision,
            regional=regional,
            busqueda=busqueda,
        )

        materia_ids = {c['materia_id'] for c in calificaciones}
        materias_map: dict[uuid.UUID, str] = {}
        if materia_ids:
            from sqlalchemy import select
            from app.models.materia import Materia
            stmt = select(Materia.id, Materia.nombre).where(Materia.id.in_(materia_ids))
            result = await self._session.execute(stmt)
            for row in result.all():
                materias_map[row[0]] = row[1]

        result = []
        for c in calificaciones:
            result.append(MonitorEntry(
                entrada_padron_id=c['entrada_padron_id'],
                nombre=c['nombre'],
                apellidos=c['apellidos'],
                comision=c['comision'],
                regional=c['regional'],
                materia_id=c['materia_id'],
                materia_nombre=materias_map.get(c['materia_id'], ''),
                actividad=c['actividad'],
                nota_numerica=float(c['nota_numerica']) if c.get('nota_numerica') is not None else None,
                nota_textual=c.get('nota_textual'),
                aprobado=None,
                importado_at=c.get('importado_at'),
            ))

        return result

    async def monitor_seguimiento(
        self,
        usuario_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        comision: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        min_actividades: int | None = None,
        busqueda: str | None = None,
    ) -> list[MonitorSeguimiento]:
        calificaciones = await self._analisis_repo.get_calificaciones_por_asignaciones(
            usuario_id=usuario_id,
            materia_id=materia_id,
            comision=comision,
            desde=desde,
            hasta=hasta,
            busqueda=busqueda,
        )

        if min_actividades is not None and calificaciones:
            alumno_aprobadas: dict[uuid.UUID, int] = {}
            for c in calificaciones:
                ep_id = c['entrada_padron_id']
                alumno_aprobadas[ep_id] = alumno_aprobadas.get(ep_id, 0) + 1
            ep_ids_validos = {
                ep_id for ep_id, count in alumno_aprobadas.items()
                if count >= min_actividades
            }
            calificaciones = [c for c in calificaciones if c['entrada_padron_id'] in ep_ids_validos]

        result = []
        for c in calificaciones:
            result.append(MonitorSeguimiento(
                entrada_padron_id=c['entrada_padron_id'],
                nombre=c['nombre'],
                apellidos=c['apellidos'],
                comision=c['comision'],
                materia_id=c['materia_id'],
                actividad=c['actividad'],
                nota_numerica=float(c['nota_numerica']) if c.get('nota_numerica') is not None else None,
                nota_textual=c.get('nota_textual'),
                aprobado=None,
                importado_at=c.get('importado_at'),
            ))

        return result

    def to_csv(self, headers: list[str], rows: list[list]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
