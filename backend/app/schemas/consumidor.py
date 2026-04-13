from typing import List, Optional

from pydantic import BaseModel, Field


# ── Base ──────────────────────────────────────────────────────────────────────

class ConsumidorBase(BaseModel):
    nome_consumidor: str = Field(..., min_length=1, max_length=255)
    prefixo_cep: str = Field(..., min_length=1, max_length=10)
    cidade: str = Field(..., min_length=1, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)


# ── Create / Update ───────────────────────────────────────────────────────────

class ConsumidorCreate(ConsumidorBase):
    pass


class ConsumidorUpdate(BaseModel):
    nome_consumidor: Optional[str] = Field(None, min_length=1, max_length=255)
    prefixo_cep: Optional[str] = Field(None, min_length=1, max_length=10)
    cidade: Optional[str] = Field(None, min_length=1, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)


# ── Response ──────────────────────────────────────────────────────────────────

class ConsumidorResponse(ConsumidorBase):
    id_consumidor: str

    model_config = {"from_attributes": True}


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedConsumidores(BaseModel):
    items: List[ConsumidorResponse]
    total: int
    page: int
    page_size: int
    pages: int
