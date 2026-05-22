import uuid
from sqlalchemy import Text, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class PostLog(Base, TimestampMixin):
    __tablename__ = "post_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationship
    post: Mapped["Post"] = relationship("Post", back_populates="logs")

    def __repr__(self) -> str:
        return f"<PostLog post={self.post_id} event={self.event}>"