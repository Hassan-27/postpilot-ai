import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.post import Post, PostStatus
from app.models.post_log import PostLog
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_post_logs(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[PostLog]:
    """Get all logs for a specific post — verifies ownership first."""
    # Verify the post belongs to this user
    post_result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == user_id)
    )
    post = post_result.scalar_one_or_none()

    if not post:
        raise ValueError("Post not found")

    result = await db.execute(
        select(PostLog)
        .where(PostLog.post_id == post_id)
        .order_by(PostLog.created_at.desc())
    )
    return list(result.scalars().all())


async def get_analytics_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> dict:
    """Get a summary of all posts for the current user."""

    # Total posts
    total = await db.execute(
        select(func.count(Post.id)).where(Post.user_id == user_id)
    )

    # By status
    published = await db.execute(
        select(func.count(Post.id)).where(
            Post.user_id == user_id,
            Post.status == PostStatus.PUBLISHED
        )
    )
    failed = await db.execute(
        select(func.count(Post.id)).where(
            Post.user_id == user_id,
            Post.status == PostStatus.FAILED
        )
    )
    scheduled = await db.execute(
        select(func.count(Post.id)).where(
            Post.user_id == user_id,
            Post.status == PostStatus.SCHEDULED
        )
    )
    drafts = await db.execute(
        select(func.count(Post.id)).where(
            Post.user_id == user_id,
            Post.status == PostStatus.DRAFT
        )
    )
    ai_generated = await db.execute(
        select(func.count(Post.id)).where(
            Post.user_id == user_id,
            Post.ai_generated == True  # noqa: E712
        )
    )

    return {
        "total_posts": total.scalar() or 0,
        "published": published.scalar() or 0,
        "failed": failed.scalar() or 0,
        "scheduled": scheduled.scalar() or 0,
        "drafts": drafts.scalar() or 0,
        "ai_generated": ai_generated.scalar() or 0,
    }