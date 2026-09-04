from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db.knowledge_schemas import KnowledgeCreate, KnowledgeRead
from app.db.models import KnowledgeDocument, User


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


@router.post(
    "/",
    response_model=KnowledgeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge(
    document_data: KnowledgeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = KnowledgeDocument(
        user_id=current_user.id,
        title=document_data.title,
        content=document_data.content,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get(
    "/",
    response_model=list[KnowledgeRead],
)
def get_knowledge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.scalars(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.user_id == current_user.id)
        .order_by(KnowledgeDocument.id)
    ).all()

    return documents


@router.get(
    "/{document_id}",
    response_model=KnowledgeRead,
)
def get_knowledge_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found.",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.user_id == current_user.id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found.",
        )

    db.delete(document)
    db.commit()

    return None