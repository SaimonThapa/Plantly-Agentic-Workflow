from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def create_app() -> FastAPI:
    app = FastAPI(title="Plantly API", version="0.1.0")
    app.include_router(router)
    app.add_api_route("/health", health, include_in_schema=False)
    return app


app = create_app()
