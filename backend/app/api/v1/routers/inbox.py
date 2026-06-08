import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import UserContext
from app.schemas.inbox import (
    HiloListResponse,
    MensajeResponse,
    NuevoMensajeRequest,
    ReplyRequest,
)
from app.services.inbox import InboxService

router = APIRouter(prefix='/api/v1/inbox')


@router.get('', response_model=HiloListResponse)
async def list_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> HiloListResponse:
    svc = InboxService(db, current_user.tenant_id)
    return await svc.list_threads(current_user.user_id)


@router.get('/{thread_id}')
async def read_thread(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> dict:
    svc = InboxService(db, current_user.tenant_id)
    return await svc.read_thread(current_user.user_id, thread_id)


@router.post('/{thread_id}/reply', response_model=MensajeResponse)
async def reply_to_thread(
    thread_id: uuid.UUID,
    body: ReplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> MensajeResponse:
    svc = InboxService(db, current_user.tenant_id)
    return await svc.reply_to_thread(current_user.user_id, thread_id, body.body)


@router.post('', status_code=201)
async def send_new_message(
    body: NuevoMensajeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> dict:
    svc = InboxService(db, current_user.tenant_id)
    return await svc.send_new_message(current_user.user_id, body)
