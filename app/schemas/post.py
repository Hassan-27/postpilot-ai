from pydantic import BaseModel
from typing import Optional
import uuid
from app.models.post import PostStatus


class PostCreate(BaseModel):
    content: str
    ai_generated: bool = False


class PostUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[PostStatus] = None


class PostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    status: PostStatus
    ai_generated: bool
    linkedin_post_id: Optional[str] = None

    model_config = {"from_attributes": True}