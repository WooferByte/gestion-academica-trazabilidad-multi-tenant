import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.mensaje_repository import MensajeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.inbox import (
    HiloListResponse,
    HiloResponse,
    MensajeResponse,
    NuevoMensajeRequest,
    ReplyRequest,
)


class InboxService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._msg_repo = MensajeRepository(session, tenant_id)
        self._user_repo = UserRepository(session, tenant_id)

    async def list_threads(self, user_id: uuid.UUID) -> HiloListResponse:
        threads = await self._msg_repo.get_threads_for_user(user_id)
        items = []
        for thread in threads:
            unread = await self._msg_repo.get_unread_count(thread.id, user_id)
            messages = await self._msg_repo.get_messages(thread.id)
            last_msg = messages[-1] if messages else None
            items.append(
                HiloResponse(
                    id=thread.id,
                    subject=thread.subject,
                    participant_ids=[uuid.UUID(pid) for pid in thread.participant_user_ids],
                    last_message_preview=last_msg.body[:100] if last_msg else None,
                    last_message_at=thread.last_message_at,
                    unread_count=unread,
                    created_at=thread.created_at,
                    updated_at=thread.updated_at,
                )
            )
        return HiloListResponse(items=items, total=len(items))

    async def read_thread(self, user_id: uuid.UUID, thread_id: uuid.UUID) -> dict:
        thread = await self._msg_repo.get_thread_for_user(thread_id, user_id)
        if not thread:
            raise HTTPException(status_code=404, detail='Hilo no encontrado')

        messages = await self._msg_repo.get_messages(thread_id)
        await self._msg_repo.mark_as_read(thread_id, user_id)

        message_responses = []
        for msg in messages:
            sender = await self._user_repo.get(msg.sender_id)
            message_responses.append(
                MensajeResponse(
                    id=msg.id,
                    hilo_id=msg.hilo_id,
                    sender_id=msg.sender_id,
                    sender_nombre=sender.email if sender else None,
                    body=msg.body,
                    read_at=msg.read_at,
                    created_at=msg.created_at,
                )
            )

        return {
            'id': str(thread.id),
            'subject': thread.subject,
            'messages': [m.model_dump() for m in message_responses],
        }

    async def reply_to_thread(
        self, user_id: uuid.UUID, thread_id: uuid.UUID, body: str,
    ) -> MensajeResponse:
        thread = await self._msg_repo.get_thread_for_user(thread_id, user_id)
        if not thread:
            raise HTTPException(status_code=404, detail='Hilo no encontrado')

        msg = await self._msg_repo.create_message(thread_id, user_id, body)
        sender = await self._user_repo.get(user_id)
        return MensajeResponse(
            id=msg.id,
            hilo_id=msg.hilo_id,
            sender_id=msg.sender_id,
            sender_nombre=sender.email if sender else None,
            body=msg.body,
            read_at=msg.read_at,
            created_at=msg.created_at,
        )

    async def send_new_message(
        self, sender_id: uuid.UUID, data: NuevoMensajeRequest,
    ) -> dict:
        recipient = await self._user_repo.get(data.recipient_id)
        if not recipient:
            raise HTTPException(status_code=404, detail='Destinatario no encontrado')

        thread = await self._msg_repo.get_or_create_thread(
            [sender_id, data.recipient_id], data.subject,
        )

        msg = await self._msg_repo.create_message(thread.id, sender_id, data.body)
        sender = await self._user_repo.get(sender_id)
        msg_response = MensajeResponse(
            id=msg.id,
            hilo_id=msg.hilo_id,
            sender_id=msg.sender_id,
            sender_nombre=sender.email if sender else None,
            body=msg.body,
            read_at=msg.read_at,
            created_at=msg.created_at,
        )

        return {
            'id': str(thread.id),
            'subject': thread.subject,
            'messages': [msg_response.model_dump()],
        }
