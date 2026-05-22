from __future__ import annotations
import uuid
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # LinkedIn OAuth tokens
    linkedin_access_token: Mapped[str] = mapped_column(Text, nullable=True)
    linkedin_token_expires_at: Mapped[str] = mapped_column(String(50), nullable=True)
    linkedin_user_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"