from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.openai_provider import OpenAIProvider
from app.ai.service import AIService
from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import Conversation, Message, User


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class AIChatRequest(BaseModel):
    conversation_id: int
    message: str = Field(min_length=1)


class AIChatResponse(BaseModel):
    conversation_id: int
    user_message: str
    assistant_message: str


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def chat(
    chat_data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
            Conversation.id == chat_data.conversation_id,
            Conversation.user_id == current_user.id,
        ).first()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_data.message,
    )

    db.add(user_message)
    db.flush()

    service = AIService(
        provider=OpenAIProvider(),
    )

    try:
        assistant_response = service.generate_response(
            chat_data.message,
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider request failed.",
        ) from exc

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_response,
    )

    db.add(assistant_message)
    db.commit()

    return AIChatResponse(
        conversation_id=conversation.id,
        user_message=chat_data.message,
        assistant_message=assistant_response,
    )