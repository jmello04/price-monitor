"""REST endpoints for product monitoring."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.schemas import (
    PriceHistoryItem,
    ProductCreate,
    ProductHistoryResponse,
    ProductResponse,
)
from app.infra.database.session import get_db
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Produtos"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar produto para monitoramento",
)
def criar_produto(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductResponse:
    """Register a new product for automated price monitoring.

    Args:
        payload: Validated product creation data.
        db: Injected database session.

    Returns:
        The created product resource.
    """
    return ProductService.create(db, payload)


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Listar produtos monitorados",
)
def listar_produtos(db: Session = Depends(get_db)) -> List[ProductResponse]:
    """List all currently active monitored products.

    Args:
        db: Injected database session.

    Returns:
        List of active product resources.
    """
    return ProductService.list_active(db)


@router.get(
    "/{product_id}/history",
    response_model=ProductHistoryResponse,
    summary="Histórico de preços de um produto",
)
def historico_produto(product_id: int, db: Session = Depends(get_db)) -> ProductHistoryResponse:
    """Return the full price history for a specific product.

    Args:
        product_id: Primary key of the product.
        db: Injected database session.

    Raises:
        HTTPException: 404 if the product does not exist.

    Returns:
        Aggregated price history including min, max and current price.
    """
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    history = ProductService.get_price_history(db, product_id)
    prices = [h.price for h in history]

    return ProductHistoryResponse(
        product=product.name,
        current_price=product.current_price,
        lowest_price=min(prices) if prices else None,
        highest_price=max(prices) if prices else None,
        target_price=product.target_price,
        history=[
            PriceHistoryItem(price=h.price, checked_at=h.checked_at)
            for h in history
        ],
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto do monitoramento",
)
def remover_produto(product_id: int, db: Session = Depends(get_db)) -> None:
    """Soft-delete a product, excluding it from future monitoring cycles.

    Args:
        product_id: Primary key of the product to remove.
        db: Injected database session.

    Raises:
        HTTPException: 404 if the product does not exist.
    """
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    ProductService.deactivate(db, product)


@router.post(
    "/{product_id}/check",
    response_model=ProductResponse,
    summary="Disparar verificação manual de preço",
)
def verificar_preco_manual(product_id: int, db: Session = Depends(get_db)) -> ProductResponse:
    """Trigger an on-demand price check for a product.

    Args:
        product_id: Primary key of the active product to check.
        db: Injected database session.

    Raises:
        HTTPException: 404 if the product is not found or inactive.

    Returns:
        The product resource with the refreshed current price.
    """
    product = ProductService.check_price(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    return product
