import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await post_service.create_post(db, current_user.id, data)
    return post


@router.get("", response_model=list[PostResponse])
async def list_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts = await post_service.get_posts(db, current_user.id)
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await post_service.get_post(db, post_id, current_user.id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await post_service.update_post(db, post_id, current_user.id, data)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await post_service.delete_post(db, post_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")