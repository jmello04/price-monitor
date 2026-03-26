"""Service layer for product business logic."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.schemas import ProductCreate
from app.infra.database.models import PriceHistory, Product

logger = logging.getLogger(__name__)


class ProductService:
    """Encapsulates all business logic for product monitoring operations."""

    @staticmethod
    def create(db: Session, payload: ProductCreate) -> Product:
        """Create a new product and persist it to the database.

        Args:
            db: Active SQLAlchemy database session.
            payload: Validated product creation schema.

        Returns:
            The newly created Product ORM instance.
        """
        product = Product(
            name=payload.name,
            url=payload.url,
            target_price=payload.target_price,
            email=payload.email,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info("Product registered: '%s' (id=%d)", product.name, product.id)
        return product

    @staticmethod
    def list_active(db: Session) -> List[Product]:
        """Return all currently active monitored products.

        Args:
            db: Active SQLAlchemy database session.

        Returns:
            List of active Product ORM instances.
        """
        return db.query(Product).filter(Product.is_active.is_(True)).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Fetch a product by its primary key.

        Args:
            db: Active SQLAlchemy database session.
            product_id: Primary key of the product to retrieve.

        Returns:
            The Product ORM instance, or None if not found.
        """
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_active_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Fetch an active product by its primary key.

        Args:
            db: Active SQLAlchemy database session.
            product_id: Primary key of the product to retrieve.

        Returns:
            The active Product ORM instance, or None if not found or inactive.
        """
        return (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )

    @staticmethod
    def deactivate(db: Session, product: Product) -> None:
        """Soft-delete a product by marking it inactive.

        Args:
            db: Active SQLAlchemy database session.
            product: The Product ORM instance to deactivate.
        """
        product.is_active = False
        db.commit()
        logger.info("Product removed from monitoring: id=%d", product.id)

    @staticmethod
    def get_price_history(db: Session, product_id: int) -> List[PriceHistory]:
        """Retrieve all price history records for a product, newest first.

        Args:
            db: Active SQLAlchemy database session.
            product_id: Primary key of the product.

        Returns:
            List of PriceHistory ORM instances ordered by checked_at descending.
        """
        return (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.checked_at.desc())
            .all()
        )

    @staticmethod
    def check_price(db: Session, product_id: int) -> Optional[Product]:
        """Trigger an immediate price check for a product and refresh its state.

        Delegates scraping and notification logic to the scheduler task, then
        refreshes the ORM instance so the caller receives the updated price.

        Args:
            db: Active SQLAlchemy database session.
            product_id: Primary key of the product to check.

        Returns:
            The refreshed Product ORM instance, or None if not found/inactive.
        """
        from app.scheduler.tasks import check_product_price

        product = ProductService.get_active_by_id(db, product_id)
        if product is None:
            return None
        check_product_price(product_id)
        db.expire(product)
        db.refresh(product)
        return product
