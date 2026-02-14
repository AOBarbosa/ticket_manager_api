from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel

from app.core.db.engine import engine

from app.presentation.api.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.infra.orm.registry

    SQLModel.metadata.create_all(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ticket Manager",
        lifespan=lifespan
    )

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    app.include_router(users_router)

    @app.get("/items/")
    async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
        return {"token": token}

    return app
