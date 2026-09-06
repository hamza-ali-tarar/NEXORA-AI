from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.ai.exceptions import AIProviderConfigurationError
from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_me_router
from app.api.v1.conversations import router as conversations_router
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


@app.exception_handler(AIProviderConfigurationError)
async def ai_provider_configuration_exception_handler(
    request: Request,
    exc: AIProviderConfigurationError,
) -> JSONResponse:
    """Return a safe response when the AI provider is misconfigured."""

    return JSONResponse(
        status_code=503,
        content={
            "detail": "AI provider is not configured.",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Return a safe response for unexpected server errors."""

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
        },
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

app.include_router(
    conversations_router,
    prefix="/api/v1",
)

app.include_router(
    ai_router,
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
