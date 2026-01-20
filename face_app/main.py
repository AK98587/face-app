from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from face_app.router.auth import router as auth_router
from face_app.core.config import Settings

settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Face Authentication API",
        description="Authentication system using password + face recognition",
        version="1.0.0",
        #debug=settings.DEBUG
    )

    # ======================
    # CORS
    # ======================
    app.add_middleware(
        CORSMiddleware,
        #allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ======================
    # Routers
    # ======================
    app.include_router(auth_router)

    # ======================
    # Health check
    # ======================
    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "service": "face-auth",
            "version": "1.0.0"
        }

    return app


app = create_app()
