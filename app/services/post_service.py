import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate, PostUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_post(db: AsyncSession, user_id: uuid.UUID, data: PostCreate) -> Post:
    post = Post(
        user_id=user_id,
        content=data.content,
        ai_generated=data.ai_generated,
        status=PostStatus.DRAFT,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    logger.info(f"Post created: {post.id} by user {user_id}")
    return post


async def get_posts(db: AsyncSession, user_id: uuid.UUID) -> list[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
    )
    return list(result.scalars().all())


async def get_post(db: AsyncSession, post_id: uuid.UUID, user_id: uuid.UUID) -> Post | None:
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    data: PostUpdate
) -> Post | None:
    post = await get_post(db, post_id, user_id)
    if not post:
        return None

    if data.content is not None:
        post.content = data.content
    if data.status is not None:
        post.status = data.status

    await db.flush()
    await db.refresh(post)
    logger.info(f"Post updated: {post.id}")
    return post


async def delete_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    post = await get_post(db, post_id, user_id)
    if not post:
        return False

    await db.delete(post)
    await db.flush()
    logger.info(f"Post deleted: {post_id}")
    return True