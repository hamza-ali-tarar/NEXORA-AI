from app.ai.retrieval import KnowledgeRetrievalService
from app.db.models import KnowledgeDocument, User


def create_user(db, email: str) -> User:
    user = User(
        email=email,
        full_name="Test User",
        password_hash="test-hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_document(
    db,
    user_id: int,
    title: str,
    content: str,
) -> KnowledgeDocument:
    document = KnowledgeDocument(
        user_id=user_id,
        title=title,
        content=content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def test_retrieval_finds_matching_knowledge(db):
    user = create_user(
        db,
        "retrieval-match@nexora.ai",
    )

    create_document(
        db,
        user.id,
        "Python Guide",
        "Python is a programming language.",
    )

    create_document(
        db,
        user.id,
        "FastAPI Guide",
        "FastAPI is a Python web framework.",
    )

    service = KnowledgeRetrievalService(db)

    results = service.search(
        user=user,
        query="Python",
    )

    assert len(results) == 2
    assert all(document.user_id == user.id for document in results)


def test_retrieval_isolates_users(db):
    user_one = create_user(
        db,
        "retrieval-user-one@nexora.ai",
    )

    user_two = create_user(
        db,
        "retrieval-user-two@nexora.ai",
    )

    create_document(
        db,
        user_one.id,
        "Private Python Notes",
        "Private Python knowledge.",
    )

    create_document(
        db,
        user_two.id,
        "Private Python Notes",
        "Private Python knowledge.",
    )

    service = KnowledgeRetrievalService(db)

    results = service.search(
        user=user_one,
        query="Python",
    )

    assert len(results) == 1
    assert results[0].user_id == user_one.id


def test_retrieval_returns_empty_for_blank_query(db):
    user = create_user(
        db,
        "retrieval-empty@nexora.ai",
    )

    create_document(
        db,
        user.id,
        "Python Guide",
        "Python knowledge.",
    )

    service = KnowledgeRetrievalService(db)

    results = service.search(
        user=user,
        query="   ",
    )

    assert results == []


def test_retrieval_respects_limit(db):
    user = create_user(
        db,
        "retrieval-limit@nexora.ai",
    )

    for index in range(5):
        create_document(
            db,
            user.id,
            f"Python Guide {index}",
            "Python programming knowledge.",
        )

    service = KnowledgeRetrievalService(db)

    results = service.search(
        user=user,
        query="Python",
        limit=2,
    )

    assert len(results) == 2
