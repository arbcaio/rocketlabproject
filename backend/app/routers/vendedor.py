import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item_pedido import ItemPedido
from app.models.produto import Produto
from app.models.vendedor import Vendedor
from app.schemas.produto import PaginatedProdutos, ProdutoResponse
from app.schemas.vendedor import (
    PaginatedVendedores,
    VendedorCreate,
    VendedorResponse,
    VendedorUpdate,
)

router = APIRouter(prefix="/vendedores", tags=["Vendedores"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_404(id_vendedor: str, db: Session) -> Vendedor:
    v = db.get(Vendedor, id_vendedor)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendedor '{id_vendedor}' não encontrado.",
        )
    return v


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedVendedores, summary="Listar vendedores")
def listar_vendedores(
    search: Optional[str] = Query(None, description="Busca por nome ou cidade"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (UF)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = select(Vendedor)
    if search:
        t = f"%{search.lower()}%"
        q = q.where(
            func.lower(Vendedor.nome_vendedor).like(t)
            | func.lower(Vendedor.cidade).like(t)
        )
    if estado:
        q = q.where(Vendedor.estado == estado.upper())

    total = db.scalar(select(func.count()).select_from(q.subquery()))
    pages = math.ceil(total / page_size) if total else 1
    items = db.scalars(
        q.order_by(Vendedor.nome_vendedor)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PaginatedVendedores(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@router.get("/{id_vendedor}", response_model=VendedorResponse, summary="Detalhar vendedor")
def obter_vendedor(id_vendedor: str, db: Session = Depends(get_db)):
    return _get_or_404(id_vendedor, db)


@router.post(
    "", response_model=VendedorResponse,
    status_code=status.HTTP_201_CREATED, summary="Criar vendedor"
)
def criar_vendedor(payload: VendedorCreate, db: Session = Depends(get_db)):
    novo = Vendedor(id_vendedor=uuid.uuid4().hex, **payload.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{id_vendedor}", response_model=VendedorResponse, summary="Atualizar vendedor")
def atualizar_vendedor(
    id_vendedor: str, payload: VendedorUpdate, db: Session = Depends(get_db)
):
    v = _get_or_404(id_vendedor, db)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(v, campo, valor)
    db.commit()
    db.refresh(v)
    return v


@router.delete("/{id_vendedor}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover vendedor")
def deletar_vendedor(id_vendedor: str, db: Session = Depends(get_db)):
    v = _get_or_404(id_vendedor, db)
    db.delete(v)
    db.commit()


@router.get(
    "/{id_vendedor}/produtos", response_model=PaginatedProdutos,
    summary="Produtos do vendedor"
)
def produtos_do_vendedor(
    id_vendedor: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retorna os produtos distintos vendidos por este vendedor."""
    _get_or_404(id_vendedor, db)

    produto_ids = (
        select(ItemPedido.id_produto)
        .where(ItemPedido.id_vendedor == id_vendedor)
        .distinct()
    )
    q = select(Produto).where(Produto.id_produto.in_(produto_ids))

    total = db.scalar(select(func.count()).select_from(q.subquery()))
    pages = math.ceil(total / page_size) if total else 1
    produtos = db.scalars(
        q.order_by(Produto.nome_produto)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        ProdutoResponse(
            id_produto=p.id_produto,
            nome_produto=p.nome_produto,
            categoria_produto=p.categoria_produto,
            peso_produto_gramas=p.peso_produto_gramas,
            comprimento_centimetros=p.comprimento_centimetros,
            altura_centimetros=p.altura_centimetros,
            largura_centimetros=p.largura_centimetros,
        )
        for p in produtos
    ]
    return PaginatedProdutos(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )
