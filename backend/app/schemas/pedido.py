from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Item de Pedido ────────────────────────────────────────────────────────────

class ItemPedidoCreate(BaseModel):
    id_produto: str
    id_vendedor: str
    preco_BRL: float = Field(..., gt=0)
    preco_frete: float = Field(..., ge=0)


class ItemPedidoResponse(BaseModel):
    id_item: int
    id_produto: str
    id_vendedor: str
    preco_BRL: float
    preco_frete: float

    model_config = {"from_attributes": True}


# ── Avaliação ─────────────────────────────────────────────────────────────────

class AvaliacaoCreate(BaseModel):
    avaliacao: int = Field(..., ge=1, le=5)
    titulo_comentario: Optional[str] = Field(None, max_length=255)
    comentario: Optional[str] = Field(None, max_length=1000)


class AvaliacaoResponse(BaseModel):
    id_avaliacao: str
    id_pedido: str
    avaliacao: int
    titulo_comentario: Optional[str] = None
    comentario: Optional[str] = None
    data_comentario: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Pedido ────────────────────────────────────────────────────────────────────

class PedidoCreate(BaseModel):
    id_consumidor: str
    status: str = Field("pendente", min_length=1, max_length=50)
    itens: List[ItemPedidoCreate] = Field(..., min_length=1)


class PedidoUpdate(BaseModel):
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    pedido_entregue_timestamp: Optional[datetime] = None
    tempo_entrega_dias: Optional[float] = Field(None, ge=0)


class PedidoResponse(BaseModel):
    id_pedido: str
    id_consumidor: str
    status: str
    pedido_compra_timestamp: Optional[datetime] = None
    pedido_entregue_timestamp: Optional[datetime] = None
    data_estimada_entrega: Optional[date] = None
    tempo_entrega_dias: Optional[float] = None

    model_config = {"from_attributes": True}


class PedidoDetalhe(PedidoResponse):
    itens: List[ItemPedidoResponse] = []
    total_itens: int = 0
    valor_total: float = 0.0
    avaliacao: Optional[AvaliacaoResponse] = None


# ── Paginação ─────────────────────────────────────────────────────────────────

class PaginatedPedidos(BaseModel):
    items: List[PedidoResponse]
    total: int
    page: int
    page_size: int
    pages: int
