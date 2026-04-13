import math
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.consumidor import Consumidor
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.schemas.pedido import (
    AvaliacaoCreate,
    AvaliacaoResponse,
    ItemPedidoResponse,
    PaginatedPedidos,
    PedidoCreate,
    PedidoDetalhe,
    PedidoResponse,
    PedidoUpdate,
)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_404(id_pedido: str, db: Session) -> Pedido:
    p = db.get(Pedido, id_pedido)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido '{id_pedido}' não encontrado.",
        )
    return p


def _build_detalhe(pedido: Pedido) -> PedidoDetalhe:
    itens = [ItemPedidoResponse.model_validate(i) for i in pedido.itens_pedidos]
    valor_total = round(sum(i.preco_BRL + i.preco_frete for i in pedido.itens_pedidos), 2)
    avaliacao = (
        AvaliacaoResponse.model_validate(pedido.avaliacao) if pedido.avaliacao else None
    )
    return PedidoDetalhe(
        id_pedido=pedido.id_pedido,
        id_consumidor=pedido.id_consumidor,
        status=pedido.status,
        pedido_compra_timestamp=pedido.pedido_compra_timestamp,
        pedido_entregue_timestamp=pedido.pedido_entregue_timestamp,
        data_estimada_entrega=pedido.data_estimada_entrega,
        tempo_entrega_dias=pedido.tempo_entrega_dias,
        itens=itens,
        total_itens=len(itens),
        valor_total=valor_total,
        avaliacao=avaliacao,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedPedidos, summary="Listar pedidos")
def listar_pedidos(
    filtro_status: Optional[str] = Query(None, alias="status"),
    id_consumidor: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = select(Pedido)
    if filtro_status:
        q = q.where(Pedido.status == filtro_status)
    if id_consumidor:
        q = q.where(Pedido.id_consumidor == id_consumidor)

    total = db.scalar(select(func.count()).select_from(q.subquery()))
    pages = math.ceil(total / page_size) if total else 1
    items = db.scalars(q.offset((page - 1) * page_size).limit(page_size)).all()
    return PaginatedPedidos(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@router.get("/{id_pedido}", response_model=PedidoDetalhe, summary="Detalhar pedido")
def obter_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.scalar(
        select(Pedido)
        .where(Pedido.id_pedido == id_pedido)
        .options(
            selectinload(Pedido.itens_pedidos),
            selectinload(Pedido.avaliacao),
        )
    )
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido '{id_pedido}' não encontrado.",
        )
    return _build_detalhe(pedido)


@router.post(
    "", response_model=PedidoDetalhe,
    status_code=status.HTTP_201_CREATED, summary="Criar pedido"
)
def criar_pedido(payload: PedidoCreate, db: Session = Depends(get_db)):
    if not db.get(Consumidor, payload.id_consumidor):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumidor '{payload.id_consumidor}' não encontrado.",
        )

    id_pedido = uuid.uuid4().hex
    ts = datetime.now(timezone.utc)

    pedido = Pedido(
        id_pedido=id_pedido,
        id_consumidor=payload.id_consumidor,
        status=payload.status,
        pedido_compra_timestamp=ts,
    )
    db.add(pedido)
    db.flush()

    itens_obj = []
    for idx, item_data in enumerate(payload.itens, start=1):
        item = ItemPedido(
            id_pedido=id_pedido,
            id_item=idx,
            id_produto=item_data.id_produto,
            id_vendedor=item_data.id_vendedor,
            preco_BRL=item_data.preco_BRL,
            preco_frete=item_data.preco_frete,
        )
        db.add(item)
        itens_obj.append(item)

    db.commit()

    itens_resp = [
        ItemPedidoResponse(
            id_item=idx,
            id_produto=d.id_produto,
            id_vendedor=d.id_vendedor,
            preco_BRL=d.preco_BRL,
            preco_frete=d.preco_frete,
        )
        for idx, d in enumerate(payload.itens, start=1)
    ]
    valor_total = round(sum(i.preco_BRL + i.preco_frete for i in payload.itens), 2)

    return PedidoDetalhe(
        id_pedido=id_pedido,
        id_consumidor=payload.id_consumidor,
        status=payload.status,
        pedido_compra_timestamp=ts,
        itens=itens_resp,
        total_itens=len(itens_resp),
        valor_total=valor_total,
    )


@router.put("/{id_pedido}", response_model=PedidoResponse, summary="Atualizar pedido")
def atualizar_pedido(
    id_pedido: str, payload: PedidoUpdate, db: Session = Depends(get_db)
):
    pedido = _get_or_404(id_pedido, db)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(pedido, campo, valor)
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{id_pedido}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover pedido")
def deletar_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = _get_or_404(id_pedido, db)
    db.delete(pedido)
    db.commit()


@router.post(
    "/{id_pedido}/avaliacao", response_model=AvaliacaoResponse,
    status_code=status.HTTP_201_CREATED, summary="Criar avaliação do pedido"
)
def criar_avaliacao(
    id_pedido: str, payload: AvaliacaoCreate, db: Session = Depends(get_db)
):
    _get_or_404(id_pedido, db)

    existente = db.scalar(
        select(AvaliacaoPedido).where(AvaliacaoPedido.id_pedido == id_pedido)
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este pedido já possui uma avaliação.",
        )

    aval = AvaliacaoPedido(
        id_avaliacao=uuid.uuid4().hex,
        id_pedido=id_pedido,
        avaliacao=payload.avaliacao,
        titulo_comentario=payload.titulo_comentario,
        comentario=payload.comentario,
        data_comentario=datetime.now(timezone.utc),
    )
    db.add(aval)
    db.commit()
    db.refresh(aval)
    return aval
