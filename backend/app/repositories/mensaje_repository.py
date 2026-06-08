import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.models.mensaje import Mensaje, MensajeHilo
from app.repositories.base import BaseRepository


class MensajeRepository(BaseRepository[MensajeHilo]):
    __model__ = MensajeHilo

    async def get_threads_for_user(self, user_id: uuid.UUID) -> Sequence[MensajeHilo]:
        stmt = (
            self._stmt()
            .where(
                MensajeHilo.participant_user_ids.contains([str(user_id)]),
            )
            .order_by(MensajeHilo.last_message_at.desc().nullslast())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_thread(self, thread_id: uuid.UUID) -> MensajeHilo | None:
        return await self.get(thread_id)

    async def get_thread_for_user(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> MensajeHilo | None:
        stmt = (
            self._stmt()
            .where(MensajeHilo.id == thread_id)
            .where(MensajeHilo.participant_user_ids.contains([str(user_id)]))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_messages(self, thread_id: uuid.UUID) -> Sequence[Mensaje]:
        stmt = (
            select(Mensaje)
            .where(Mensaje.hilo_id == thread_id)
            .where(Mensaje.tenant_id == self._tenant_id)
            .where(Mensaje.deleted_at.is_(None))
            .order_by(Mensaje.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_message(
        self, hilo_id: uuid.UUID, sender_id: uuid.UUID, body: str,
    ) -> Mensaje:
        msg = Mensaje(
            tenant_id=self._tenant_id,
            hilo_id=hilo_id,
            sender_id=sender_id,
            body=body,
        )
        self._session.add(msg)
        await self._session.flush()

        stmt = (
            update(MensajeHilo)
            .where(MensajeHilo.id == hilo_id)
            .where(MensajeHilo.tenant_id == self._tenant_id)
            .values(last_message_at=msg.created_at)
        )
        await self._session.execute(stmt)
        await self._session.flush()

        return msg

    async def get_or_create_thread(
        self, participant_ids: list[uuid.UUID], subject: str,
    ) -> MensajeHilo:
        str_ids = [str(pid) for pid in participant_ids]
        stmt = (
            self._stmt()
            .where(MensajeHilo.participant_user_ids.contains([str_ids[0]]))
        )
        result = await self._session.execute(stmt)
        existing = result.scalars().all()

        for thread in existing:
            if set(thread.participant_user_ids) == set(str_ids):
                return thread

        hilo = MensajeHilo(
            tenant_id=self._tenant_id,
            participant_user_ids=str_ids,
            subject=subject,
        )
        self._session.add(hilo)
        await self._session.flush()
        return hilo

    async def mark_as_read(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> None:
        stmt = (
            update(Mensaje)
            .where(Mensaje.hilo_id == thread_id)
            .where(Mensaje.tenant_id == self._tenant_id)
            .where(Mensaje.sender_id != user_id)
            .where(Mensaje.read_at.is_(None))
            .where(Mensaje.deleted_at.is_(None))
            .values(read_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_unread_count(self, thread_id: uuid.UUID, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Mensaje)
            .where(Mensaje.hilo_id == thread_id)
            .where(Mensaje.tenant_id == self._tenant_id)
            .where(Mensaje.sender_id != user_id)
            .where(Mensaje.read_at.is_(None))
            .where(Mensaje.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_message_by_id(self, message_id: uuid.UUID) -> Mensaje | None:
        stmt = (
            select(Mensaje)
            .where(Mensaje.id == message_id)
            .where(Mensaje.tenant_id == self._tenant_id)
            .where(Mensaje.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
