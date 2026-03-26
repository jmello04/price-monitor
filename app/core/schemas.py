"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


class ProductCreate(BaseModel):
    """Schema for creating a new monitored product.

    Attributes:
        name: Human-readable product name.
        url: Full product page URL (must start with http:// or https://).
        target_price: Desired price threshold; alert is sent when price drops to or below this value.
        email: Email address that receives price-drop notifications.
    """

    name: str
    url: str
    target_price: float
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Reject blank or whitespace-only product names.

        Args:
            v: Raw name value from the request body.

        Returns:
            Stripped name string.

        Raises:
            ValueError: If the name is empty after stripping whitespace.
        """
        if not v.strip():
            raise ValueError("O nome do produto não pode ser vazio.")
        return v.strip()

    @field_validator("target_price")
    @classmethod
    def target_price_positive(cls, v: float) -> float:
        """Ensure the target price is a positive number.

        Args:
            v: Raw target_price value from the request body.

        Returns:
            The validated price value.

        Raises:
            ValueError: If the price is zero or negative.
        """
        if v <= 0:
            raise ValueError("O preço alvo deve ser maior que zero.")
        return v

    @field_validator("url")
    @classmethod
    def url_has_scheme(cls, v: str) -> str:
        """Validate that the URL begins with an accepted scheme.

        Args:
            v: Raw URL value from the request body.

        Returns:
            The validated URL string.

        Raises:
            ValueError: If the URL does not start with http:// or https://.
        """
        if not v.startswith(("http://", "https://")):
            raise ValueError("A URL deve começar com http:// ou https://.")
        return v


class ProductResponse(BaseModel):
    """Schema for serializing a product resource in API responses.

    Attributes:
        id: Database primary key.
        name: Product name.
        url: Product page URL.
        target_price: Configured price alert threshold.
        email: Notification email address.
        current_price: Most recently scraped price, or None if not yet checked.
        is_active: Whether the product is still being monitored.
        created_at: UTC timestamp of product registration.
    """

    id: int
    name: str
    url: str
    target_price: float
    email: str
    current_price: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryItem(BaseModel):
    """A single price observation.

    Attributes:
        price: Scraped price value in BRL.
        checked_at: UTC timestamp when this observation was recorded.
    """

    price: float
    checked_at: datetime


class ProductHistoryResponse(BaseModel):
    """Aggregated price history for a product.

    Attributes:
        product: Product name.
        current_price: Most recently scraped price.
        lowest_price: Lowest price ever recorded for this product.
        highest_price: Highest price ever recorded for this product.
        target_price: Configured alert threshold.
        history: Chronologically ordered list of price observations.
    """

    product: str
    current_price: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    target_price: float
    history: List[PriceHistoryItem]
