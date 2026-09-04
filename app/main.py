from fastapi import FastAPI

from app.api.v1.auth import router as auth_me_router
from app.api.v1.health import router as health_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.users import router as users_router
from app.auth.auth import router as auth_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    auth_me_router,
    prefix="/api/v1",
)

app.include_router(
    knowledge_router,
    prefix="/api/v1",
)


@app.get("/", tags=["Root"])
def home():
    return {
        "name": settings.APP_NAME,
        "status": "online",
        "version": settings.APP_VERSION,
        "message": "NEXORA AI foundation is working.",
    }