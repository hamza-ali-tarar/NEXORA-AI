from sqlalchemy import or_, select  # pyright: ignore[reportMissingImports]
from typing import Any

from app.db.models import KnowledgeDocument, User


class KnowledgeRetrievalService:
    """Service responsible for retrieving relevant user knowledge."""

    def __init__(self, db: Any):
        self.db = db

    def search(
        self,
        user: User,
        query: str,
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        """Retrieve knowledge documents matching relevant query words."""

        search_text = query.strip()

        if not search_text:
            return []

        words = [
            word.strip(".,!?;:()[]{}\"'")
            for word in search_text.split()
        ]

        words = [
            word
            for word in words
            if len(word) >= 3
        ]

        if not words:
            return []

        conditions = []

        for word in words:
            search_term = f"%{word}%"

            conditions.append(
                or_(
                    KnowledgeDocument.title.ilike(search_term),
                    KnowledgeDocument.content.ilike(search_term),
                )
            )

        statement = (
            select(KnowledgeDocument)
            .where(
                KnowledgeDocument.user_id == user.id,
                or_(*conditions),
            )
            .order_by(KnowledgeDocument.id.desc())
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
