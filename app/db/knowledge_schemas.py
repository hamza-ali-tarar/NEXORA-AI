from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class KnowledgeRead(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }