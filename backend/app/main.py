import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

_logger = logging.getLogger("dermassist")


def create_app() -> FastAPI:
    app = FastAPI(
        title="DermAssist AI Backend",
        description=(
            "Research prototype backend for AI-assisted early skin lesion risk screening. "
            "Not a medical diagnosis tool."
        ),
        version="0.1.0",
    )

    # Allow local frontend dev server to call the API.
    # Keep this tight for a research prototype; expand as needed for deployments.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            # Next.js picks 3001+ when the default port is busy
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.on_event("startup")
    def _log_checkpoint_startup() -> None:
        from app.models.model_loader import get_loaded_model

        loaded = get_loaded_model()
        if loaded is not None:
            msg = (
                f"DERMASSIST_CHECKPOINT loaded: {loaded.checkpoint_path} "
                f"(device={loaded.device})"
            )
            _logger.info(msg)
            print(f"[dermassist] {msg}", flush=True)
        else:
            warn = (
                "DERMASSIST_CHECKPOINT not set or load failed — "
                "/predict uses placeholder inference until configured."
            )
            _logger.warning(warn)
            print(f"[dermassist] WARNING: {warn}", flush=True)

    return app


app = create_app()

