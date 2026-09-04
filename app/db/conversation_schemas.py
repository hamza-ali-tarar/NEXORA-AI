from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ConversationRead(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    role: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)