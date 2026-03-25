import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import get_settings
from app.infra.database.models import PriceHistory, Product
from app.infra.database.session import SessionLocal
from app.notifications.email_sender import send_price_alert
from app.scraper.sites import get_scraper

logger = logging.getLogger(__name__)


def check_product_price(product_id: int) -> None:
    db = SessionLocal()
    try:
        product: Product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )
        if not product:
            logger.warning("Produto %d não encontrado ou inativo.", product_id)
            return

        scraper = get_scraper(product.url)
        if scraper is None:
            logger.warning(
                "Nenhum scraper disponível para a URL do produto %d: %s",
                product_id,
                product.url,
            )
            return

        price = scraper.scrape(product.url)
        if price is None:
            logger.warning(
                "Não foi possível obter o preço do produto '%s'.", product.name
            )
            return

        registro = PriceHistory(
            product_id=product.id,
            price=price,
            checked_at=datetime.now(timezone.utc),
        )
        db.add(registro)
        product.current_price = price
        db.commit()

        logger.info(
            "Preço atualizado — produto: '%s' | preço: R$ %.2f | alvo: R$ %.2f",
            product.name,
            price,
            product.target_price,
        )

        if price <= product.target_price:
            logger.info(
                "Preço alvo atingido para '%s'. Enviando alerta para %s.",
                product.name,
                product.email,
            )
            send_price_alert(
                product_name=product.name,
                current_price=price,
                target_price=product.target_price,
                product_url=product.url,
                recipient_email=product.email,
            )

    except Exception as exc:
        logger.error("Erro ao verificar produto %d: %s", product_id, exc)
        db.rollback()
    finally:
        db.close()


def check_all_products() -> None:
    logger.info("Iniciando verificação periódica de preços...")

    product_ids: list[int] = []
    db = SessionLocal()
    try:
        product_ids = [
            row.id
            for row in db.query(Product.id)
            .filter(Product.is_active.is_(True))
            .all()
        ]
    except Exception as exc:
        logger.error("Erro ao buscar lista de produtos: %s", exc)
    finally:
        db.close()

    for pid in product_ids:
        check_product_price(pid)

    logger.info(
        "Verificação periódica concluída. Total: %d produto(s).", len(product_ids)
    )


def create_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        func=check_all_products,
        trigger=IntervalTrigger(hours=settings.CHECK_INTERVAL_HOURS),
        id="verificacao_periodica_de_precos",
        name="Verificação periódica de preços",
        replace_existing=True,
    )
    return scheduler
