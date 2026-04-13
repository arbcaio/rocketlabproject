from typing import List, Optional

from pydantic import BaseModel, Field


# ── Base ──────────────────────────────────────────────────────────────────────

class VendedorBase(BaseModel):
    nome_vendedor: str = Field(..., min_length=1, max_length=255)
    prefixo_cep: str = Field(..., min_length=1, max_length=10)
    cidade: str = Field(..., min_length=1, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)


# ── Create / Update ───────────────────────────────────────────────────────────

class VendedorCreate(VendedorBase):
    pass


class VendedorUpdate(BaseModel):
    nome_vendedor: Optional[str] = Field(None, min_length=1, max_length=255)
    prefixo_cep: Optional[str] = Field(None, min_length=1, max_length=10)
    cidade: Optional[str] = Field(None, min_length=1, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)


# ── Response ──────────────────────────────────────────────────────────────────

class VendedorResponse(VendedorBase):
    id_vendedor: str

    model_config = {"from_attributes": True}


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedVendedores(BaseModel):
    items: List[VendedorResponse]
    total: int
    page: int
    page_size: int
    pages: int
