"""SQLAlchemy ORM models for the price monitoring domain."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infra.database.session import Base


def _utcnow() -> datetime:
    """Return the current UTC datetime.

    Returns:
        Timezone-aware datetime set to UTC.
    """
    return datetime.now(timezone.utc)


class Product(Base):
    """Represents a product registered for price monitoring.

    Attributes:
        id: Auto-incremented primary key.
        name: Human-readable product name.
        url: Full URL of the product page used for scraping.
        target_price: Price threshold that triggers an email alert.
        email: Recipient address for price-drop notifications.
        current_price: Last scraped price; None until the first check.
        is_active: False when the product has been soft-deleted.
        created_at: UTC timestamp of registration.
        price_history: All recorded price observations for this product.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    target_price = Column(Float, nullable=False)
    email = Column(String(255), nullable=False)
    current_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    price_history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select",
    )


class PriceHistory(Base):
    """Records a single price observation for a product.

    Attributes:
        id: Auto-incremented primary key.
        product_id: Foreign key referencing the monitored product.
        price: Scraped price value at the time of the check.
        checked_at: UTC timestamp when the price was recorded.
        product: Back-reference to the owning Product instance.
    """

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    checked_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    product = relationship("Product", back_populates="price_history")
