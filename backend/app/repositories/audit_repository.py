import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    async def create(self, entry: AuditLog) -> AuditLog:
        self._session.add(entry)
        await self._session.flush()
        return entry
