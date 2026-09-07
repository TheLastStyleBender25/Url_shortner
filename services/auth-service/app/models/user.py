from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:Mapped[str] = mapped_column(String(255), nullable=False)
    email:Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash:Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified:Mapped[bool] = mapped_column(Boolean, default=False)
    created_at:Mapped[bool] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[bool] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())