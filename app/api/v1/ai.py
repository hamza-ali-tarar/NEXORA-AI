from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]

from app.ai.openai_provider import OpenAIProvider
from app.ai.retrieval import KnowledgeRetrievalService
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


def build_knowledge_context(documents) -> str:
    """Build a readable knowledge context for the AI provider."""

    return "\n\n".join(
        (
            f"Title: {document.title}\n"
            f"Content: {document.content}"
        )
        for document in documents
    )


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def chat(
    chat_data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == chat_data.conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

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

    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation.id,
        )
        .order_by(Message.id)
    ).all()

    conversation_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    try:
        retrieval_service = KnowledgeRetrievalService(db)

        relevant_documents = retrieval_service.search(
            user=current_user,
            query=chat_data.message,
            limit=5,
        )

        knowledge_context = build_knowledge_context(
            relevant_documents,
        )

        service = AIService(
            provider=OpenAIProvider(),
        )

        assistant_response = service.generate_conversation_response(
            conversation_messages,
            knowledge_context=knowledge_context or None,
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
