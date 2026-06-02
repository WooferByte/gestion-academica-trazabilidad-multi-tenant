import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.schemas.auth import UserContext


class AuditService:
    def __init__(
        self,
        session: AsyncSession,
        user_context: UserContext,
        ip: str = 'unknown',
        user_agent: str = 'unknown',
    ):
        self._session = session
        self._user_context = user_context
        self._ip = ip
        self._user_agent = user_agent
        self._repo = AuditRepository(session, user_context.tenant_id)

    async def log(
        self,
        accion: str,
        detalle: dict | None = None,
        filas_afectadas: int = 0,
        materia_id: uuid.UUID | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=self._user_context.tenant_id,
            actor_id=self._user_context.user_id,
            impersonado_id=self._user_context.impersonator_id,
            materia_id=materia_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=filas_afectadas,
            ip=ip or self._ip,
            user_agent=user_agent or self._user_agent,
        )
        return await self._repo.create(entry)
