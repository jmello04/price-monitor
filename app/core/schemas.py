from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


class ProductCreate(BaseModel):
    name: str
    url: str
    target_price: float
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_nao_pode_ser_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("O nome do produto não pode ser vazio.")
        return v.strip()

    @field_validator("target_price")
    @classmethod
    def preco_alvo_deve_ser_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("O preço alvo deve ser maior que zero.")
        return v

    @field_validator("url")
    @classmethod
    def url_deve_ser_valida(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("A URL deve começar com http:// ou https://.")
        return v


class ProductResponse(BaseModel):
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
    price: float
    checked_at: datetime


class ProductHistoryResponse(BaseModel):
    product: str
    current_price: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    target_price: float
    history: List[PriceHistoryItem]
