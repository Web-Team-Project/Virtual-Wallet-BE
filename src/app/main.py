"""
Boot FastApi app
"""
from urllib.parse import urljoin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from app.sql_app.database import get_db
from app.api.api_v1.api import api_router
from app.core.config import get_settings
from app.services.crud.recurring_transaction import process_recurring_transactions


SECRET_KEY = "supersecretkey"
CORS = ["http://localhost:3000/", "https://global-payment-system.onrender.com/", "https://virtual-wallet-87bx.onrender.com/"]

def _setup_cors(p_app: FastAPI) -> None:
    """
    Set all CORS enabled origins
    """
    p_app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


scheduler = AsyncIOScheduler()


async def scheduled_task():
    async for db in get_db():
        try:
            await process_recurring_transactions(db)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()

scheduler.add_job(scheduled_task, "interval", minutes=10)


@asynccontextmanager
async def lifespan(p_app: FastAPI):
    print("Starting FastAPI application...")
    scheduler.start()
    yield
    print("Shutting down FastAPI application...")
    scheduler.shutdown()


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=get_settings().PROJECT_NAME,
        openapi_url=urljoin(get_settings().API_V1_STR, "openapi.json"),
        version=get_settings().VERSION,
        docs_url="/swagger",
        lifespan=lifespan
    )
    app_.include_router(
        api_router,
        prefix=get_settings().API_V1_STR,
    )

    app_.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

    return app_


app = _create_app()
_setup_cors(app)