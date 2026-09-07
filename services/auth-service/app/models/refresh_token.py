from sqlalchemy import String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id:Mapped[UUID]=mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    user_id:Mapped[UUID]=mapped_column(UUID(as_uuid=True),ForeignKey('users.id'), nullable=False)
    token_hash:Mapped[str]=mapped_column(String(255),nullable=False)
    created_at:Mapped[bool] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[bool] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())