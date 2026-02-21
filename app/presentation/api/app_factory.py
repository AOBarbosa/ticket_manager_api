from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.db.engine import engine

from app.presentation.api.routers.protected import protected_router
from app.presentation.api.routers.users import router as users_router
from app.presentation.api.routers.auth import router as auth_router
from app.presentation.api.routers.me import router as me_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.infra.orm.registry
    SQLModel.metadata.create_all(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Ticket Manager", lifespan=lifespan)

    app.include_router(auth_router)

    protected_router.include_router(users_router)
    protected_router.include_router(me_router)

    app.include_router(protected_router)

    return app