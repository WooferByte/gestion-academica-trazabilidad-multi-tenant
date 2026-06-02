from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService


async def get_audit_service(
    request: Request,
    current_user: UserContext = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AuditService, None]:
    ip = request.client.host if request.client else 'unknown'
    user_agent = request.headers.get('user-agent', 'unknown')
    service = AuditService(session, current_user, ip=ip, user_agent=user_agent)
    yield service
