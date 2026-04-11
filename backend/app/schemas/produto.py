from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Base ──────────────────────────────────────────────────────────────────────

class ProdutoBase(BaseModel):
    nome_produto: str = Field(..., min_length=1, max_length=255)
    categoria_produto: str = Field(..., min_length=1, max_length=100)
    peso_produto_gramas: Optional[float] = Field(None, gt=0)
    comprimento_centimetros: Optional[float] = Field(None, gt=0)
    altura_centimetros: Optional[float] = Field(None, gt=0)
    largura_centimetros: Optional[float] = Field(None, gt=0)


# ── Create / Update ───────────────────────────────────────────────────────────

class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome_produto: Optional[str] = Field(None, min_length=1, max_length=255)
    categoria_produto: Optional[str] = Field(None, min_length=1, max_length=100)
    peso_produto_gramas: Optional[float] = Field(None, gt=0)
    comprimento_centimetros: Optional[float] = Field(None, gt=0)
    altura_centimetros: Optional[float] = Field(None, gt=0)
    largura_centimetros: Optional[float] = Field(None, gt=0)


# ── Response ──────────────────────────────────────────────────────────────────

class ProdutoResponse(ProdutoBase):
    id_produto: str

    model_config = {"from_attributes": True}


class ProdutoDetalhe(ProdutoResponse):
    media_avaliacao: Optional[float] = None
    total_avaliacoes: int = 0
    total_vendas: int = 0
    receita_total: float = 0.0
    preco_medio: Optional[float] = None


# ── Avaliação ─────────────────────────────────────────────────────────────────

class AvaliacaoResponse(BaseModel):
    id_avaliacao: str
    avaliacao: int
    titulo_comentario: Optional[str] = None
    comentario: Optional[str] = None
    data_comentario: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedProdutos(BaseModel):
    items: List[ProdutoResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedAvaliacoes(BaseModel):
    items: List[AvaliacaoResponse]
    total: int
    page: int
    page_size: int
    pages: int
    media_avaliacao: Optional[float] = None


# ── Categorias ────────────────────────────────────────────────────────────────

class CategoriaResponse(BaseModel):
    categoria: str
    total_produtos: int
