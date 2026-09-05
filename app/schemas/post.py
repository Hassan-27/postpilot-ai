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
    

class PostGenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    audience: str = "general professionals"
    length: str = "medium (150-200 words)"
    save_as_draft: bool = False  # if True, saves to DB automatically


class PostGenerateResponse(BaseModel):
    content: str
    post_id: uuid.UUID | None = None  # set if save_as_draft=True