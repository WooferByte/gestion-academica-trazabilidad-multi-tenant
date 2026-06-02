import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class TestModel(Base, BaseModelMixin):
    __tablename__ = 'test_models'

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
