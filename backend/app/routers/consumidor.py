import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consumidor import Consumidor
from app.models.pedido import Pedido
from app.schemas.consumidor import (
    ConsumidorCreate,
    ConsumidorResponse,
    ConsumidorUpdate,
    PaginatedConsumidores,
)
from app.schemas.pedido import PaginatedPedidos

router = APIRouter(prefix="/consumidores", tags=["Consumidores"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_404(id_consumidor: str, db: Session) -> Consumidor:
    c = db.get(Consumidor, id_consumidor)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consumidor '{id_consumidor}' não encontrado.",
        )
    return c


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedConsumidores, summary="Listar consumidores")
def listar_consumidores(
    search: Optional[str] = Query(None, description="Busca por nome ou cidade"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (UF)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = select(Consumidor)
    if search:
        t = f"%{search.lower()}%"
        q = q.where(
            func.lower(Consumidor.nome_consumidor).like(t)
            | func.lower(Consumidor.cidade).like(t)
        )
    if estado:
        q = q.where(Consumidor.estado == estado.upper())

    total = db.scalar(select(func.count()).select_from(q.subquery()))
    pages = math.ceil(total / page_size) if total else 1
    items = db.scalars(
        q.order_by(Consumidor.nome_consumidor)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PaginatedConsumidores(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@router.get("/{id_consumidor}", response_model=ConsumidorResponse, summary="Detalhar consumidor")
def obter_consumidor(id_consumidor: str, db: Session = Depends(get_db)):
    return _get_or_404(id_consumidor, db)


@router.post(
    "", response_model=ConsumidorResponse,
    status_code=status.HTTP_201_CREATED, summary="Criar consumidor"
)
def criar_consumidor(payload: ConsumidorCreate, db: Session = Depends(get_db)):
    novo = Consumidor(id_consumidor=uuid.uuid4().hex, **payload.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{id_consumidor}", response_model=ConsumidorResponse, summary="Atualizar consumidor")
def atualizar_consumidor(
    id_consumidor: str, payload: ConsumidorUpdate, db: Session = Depends(get_db)
):
    c = _get_or_404(id_consumidor, db)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(c, campo, valor)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{id_consumidor}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover consumidor")
def deletar_consumidor(id_consumidor: str, db: Session = Depends(get_db)):
    c = _get_or_404(id_consumidor, db)
    db.delete(c)
    db.commit()


@router.get(
    "/{id_consumidor}/pedidos", response_model=PaginatedPedidos,
    summary="Pedidos do consumidor"
)
def pedidos_do_consumidor(
    id_consumidor: str,
    filtro_status: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    _get_or_404(id_consumidor, db)
    q = select(Pedido).where(Pedido.id_consumidor == id_consumidor)
    if filtro_status:
        q = q.where(Pedido.status == filtro_status)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    pages = math.ceil(total / page_size) if total else 1
    items = db.scalars(q.offset((page - 1) * page_size).limit(page_size)).all()
    return PaginatedPedidos(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )
