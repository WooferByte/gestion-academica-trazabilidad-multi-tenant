import uuid
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository


class GrillaSalarialService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._base_repo = SalarioBaseRepository(session, tenant_id)
        self._plus_repo = SalarioPlusRepository(session, tenant_id)

    async def crear_base(self, rol: str, monto: float, desde: date) -> SalarioBase:
        anterior = await self._base_repo.get_vigente_sin_hasta(rol)
        if anterior and anterior.desde < desde:
            dia_anterior = desde - timedelta(days=1)
            await self._base_repo.cerrar_vigencia(anterior.id, dia_anterior)
        return await self._base_repo.create(rol=rol, monto=monto, desde=desde)

    async def listar_bases(self) -> list[SalarioBase]:
        bases = await self._base_repo.list_historicos()
        return list(bases)

    async def listar_bases_vigentes(self) -> list[SalarioBase]:
        today = date.today()
        roles = ['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR']
        vigentes = []
        for rol in roles:
            base = await self._base_repo.get_vigente(rol, today)
            if base:
                vigentes.append(base)
        return vigentes

    async def crear_plus(
        self, grupo: str, rol: str, monto: float, desde: date, descripcion: str | None = None,
    ) -> SalarioPlus:
        anterior = await self._plus_repo.get_vigente_sin_hasta(grupo, rol)
        if anterior and anterior.desde < desde:
            dia_anterior = desde - timedelta(days=1)
            await self._plus_repo.cerrar_vigencia(anterior.id, dia_anterior)
        return await self._plus_repo.create(
            grupo=grupo, rol=rol, monto=monto, desde=desde, descripcion=descripcion,
        )

    async def listar_pluses(self, grupo: str | None = None) -> list[SalarioPlus]:
        pluses = await self._plus_repo.list_por_grupo(grupo=grupo)
        return list(pluses)
