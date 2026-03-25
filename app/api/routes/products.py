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
from app.infra.database.models import PriceHistory, Product
from app.infra.database.session import get_db
from app.scheduler.tasks import check_product_price

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Produtos"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar produto para monitoramento",
)
def criar_produto(payload: ProductCreate, db: Session = Depends(get_db)):
    produto = Product(
        name=payload.name,
        url=payload.url,
        target_price=payload.target_price,
        email=payload.email,
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    logger.info("Produto cadastrado: '%s' (id=%d)", produto.name, produto.id)
    return produto


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Listar produtos monitorados",
)
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active.is_(True)).all()


@router.get(
    "/{product_id}/history",
    response_model=ProductHistoryResponse,
    summary="Histórico de preços de um produto",
)
def historico_produto(product_id: int, db: Session = Depends(get_db)):
    produto = db.query(Product).filter(Product.id == product_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    historico = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.checked_at.desc())
        .all()
    )

    precos = [h.price for h in historico]

    return ProductHistoryResponse(
        product=produto.name,
        current_price=produto.current_price,
        lowest_price=min(precos) if precos else None,
        highest_price=max(precos) if precos else None,
        target_price=produto.target_price,
        history=[
            PriceHistoryItem(price=h.price, checked_at=h.checked_at)
            for h in historico
        ],
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto do monitoramento",
)
def remover_produto(product_id: int, db: Session = Depends(get_db)):
    produto = db.query(Product).filter(Product.id == product_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    produto.is_active = False
    db.commit()
    logger.info("Produto removido do monitoramento: id=%d", product_id)


@router.post(
    "/{product_id}/check",
    response_model=ProductResponse,
    summary="Disparar verificação manual de preço",
)
def verificar_preco_manual(product_id: int, db: Session = Depends(get_db)):
    produto = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active.is_(True))
        .first()
    )
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    check_product_price(product_id)
    db.expire(produto)
    db.refresh(produto)
    return produto
