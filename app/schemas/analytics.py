from pydantic import BaseModel
from datetime import datetime
import uuid


class PostLogResponse(BaseModel):
    id: uuid.UUID
    post_id: uuid.UUID
    event: str
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_posts: int
    published: int
    failed: int
    scheduled: int
    drafts: int
    ai_generated: int