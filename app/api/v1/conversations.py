from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.auth.dependencies import get_current_user
from app.db.conversation_schemas import ConversationCreate, ConversationRead
from app.db.database import get_db
from app.db.models import Conversation, User


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get(
    "/",
    response_model=list[ConversationRead],
)
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id,
        )
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
    )

    return db.scalars(query).all()


@router.get(
    "/{conversation_id}",
    response_model=ConversationRead,
)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    db.delete(conversation)
    db.commit()

    return None