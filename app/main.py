import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.products import router as products_router
from app.core.config import get_settings
from app.infra.database.session import create_tables
from app.scheduler.tasks import create_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Iniciando Price Monitor...")
    create_tables()
    scheduler = create_scheduler()
    scheduler.start()
    logger.info(
        "Scheduler iniciado. Próxima verificação em %d hora(s).",
        settings.CHECK_INTERVAL_HOURS,
    )
    yield
    scheduler.shutdown(wait=False)
    logger.info("Price Monitor encerrado.")


app = FastAPI(
    title="Price Monitor",
    description=(
        "API para monitoramento automático de preços em e-commerces. "
        "Cadastre produtos, acompanhe o histórico e receba alertas por e-mail "
        "quando o preço atingir sua meta."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(products_router)


@app.get("/health", tags=["Status"])
def health_check():
    return {"status": "ok", "service": "price-monitor", "version": "1.0.0"}
