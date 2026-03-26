"""Background scheduler tasks for periodic price checks."""

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
    """Scrape the current price for a single product and persist the result.

    Opens its own database session, performs scraping, saves the price
    observation, updates the product's current_price field, and sends an
    email alert if the price has reached or fallen below the target.

    Args:
        product_id: Primary key of the product to check.
    """
    db = SessionLocal()
    try:
        product: Product | None = (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )
        if not product:
            logger.warning("Product %d not found or inactive.", product_id)
            return

        scraper = get_scraper(product.url)
        if scraper is None:
            logger.warning(
                "No scraper available for product %d URL: %s",
                product_id,
                product.url,
            )
            return

        price = scraper.scrape(product.url)
        if price is None:
            logger.warning("Could not retrieve price for product '%s'.", product.name)
            return

        record = PriceHistory(
            product_id=product.id,
            price=price,
            checked_at=datetime.now(timezone.utc),
        )
        db.add(record)
        product.current_price = price
        db.commit()

        logger.info(
            "Price updated — product: '%s' | price: R$ %.2f | target: R$ %.2f",
            product.name,
            price,
            product.target_price,
        )

        if price <= product.target_price:
            logger.info(
                "Target price reached for '%s'. Sending alert to %s.",
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

    except (OSError, ValueError) as exc:
        logger.error("Error while checking product %d: %s", product_id, exc)
        db.rollback()
    finally:
        db.close()


def check_all_products() -> None:
    """Run a price check for every active product in the database.

    Fetches active product IDs in a short-lived session, then delegates
    each individual check to :func:`check_product_price`.
    """
    logger.info("Starting periodic price check...")

    product_ids: list[int] = []
    db = SessionLocal()
    try:
        product_ids = [
            row.id
            for row in db.query(Product.id)
            .filter(Product.is_active.is_(True))
            .all()
        ]
    except (OSError, ValueError) as exc:
        logger.error("Error fetching product list: %s", exc)
    finally:
        db.close()

    for pid in product_ids:
        check_product_price(pid)

    logger.info(
        "Periodic price check complete. Total: %d product(s).", len(product_ids)
    )


def create_scheduler() -> BackgroundScheduler:
    """Build and configure the background scheduler.

    Returns:
        A configured BackgroundScheduler instance with the periodic price
        check job registered. The caller is responsible for starting and
        stopping the scheduler.
    """
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        func=check_all_products,
        trigger=IntervalTrigger(hours=settings.CHECK_INTERVAL_HOURS),
        id="periodic_price_check",
        name="Periodic price check",
        replace_existing=True,
    )
    return scheduler
