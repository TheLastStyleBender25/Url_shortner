from app.db.base import Base
from sqlalchemy import String, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Url(Base):
    __tablename__ = 'urls'

    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    original_url:Mapped[str]=mapped_column(Text, nullable=False)
    short_code:Mapped[str]=mapped_column(String(6), nullable=False, unique=True)
    is_active:Mapped[bool]=mapped_column(Boolean, nullable=False, default=True)
    created_at:Mapped[bool] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at:Mapped[bool] = mapped_column(DateTime(timezone=True), nullable=True)

