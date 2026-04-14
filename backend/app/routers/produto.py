import math
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, case, nulls_last
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.schemas.produto import (
    AvaliacaoResponse,
    CategoriaResponse,
    PaginatedAvaliacoes,
    PaginatedProdutos,
    ProdutoCreate,
    ProdutoDetalhe,
    ProdutoResponse,
    ProdutoUpdate,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_produto_or_404(id_produto: str, db: Session) -> Produto:
    produto = db.get(Produto, id_produto)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto '{id_produto}' não encontrado.",
        )
    return produto


def _stats_para_produto(id_produto: str, db: Session) -> dict:
    """Retorna estatísticas de vendas e avaliações de um produto."""
    # Total de vendas e receita
    vendas_q = (
        db.execute(
            select(
                func.count(ItemPedido.id_item).label("total_vendas"),
                func.coalesce(func.sum(ItemPedido.preco_BRL), 0).label("receita_total"),
                func.coalesce(func.avg(ItemPedido.preco_BRL), 0).label("preco_medio"),
            ).where(ItemPedido.id_produto == id_produto)
        )
        .mappings()
        .one()
    )

    # Média e total de avaliações (via pedidos -> itens)
    aval_q = (
        db.execute(
            select(
                func.count(AvaliacaoPedido.id_avaliacao).label("total_avaliacoes"),
                func.avg(AvaliacaoPedido.avaliacao).label("media_avaliacao"),
            )
            .join(Pedido, AvaliacaoPedido.id_pedido == Pedido.id_pedido)
            .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
            .where(ItemPedido.id_produto == id_produto)
        )
        .mappings()
        .one()
    )

    return {
        "total_vendas": vendas_q["total_vendas"] or 0,
        "receita_total": round(float(vendas_q["receita_total"] or 0), 2),
        "preco_medio": round(float(vendas_q["preco_medio"] or 0), 2) if vendas_q["preco_medio"] else None,
        "total_avaliacoes": aval_q["total_avaliacoes"] or 0,
        "media_avaliacao": round(float(aval_q["media_avaliacao"]), 2) if aval_q["media_avaliacao"] else None,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedProdutos, summary="Listar produtos")
def listar_produtos(
    search: Optional[str] = Query(None, description="Busca por nome ou categoria"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    ordenar: Optional[str] = Query(None, description="Ordenação: nome | avaliacao | vendas"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista todos os produtos com suporte a busca, filtro por categoria, ordenação e paginação."""

    # ── Subquery: média e total de avaliações por produto ───────────────────
    aval_sub = (
        select(
            ItemPedido.id_produto.label("id_produto"),
            func.avg(AvaliacaoPedido.avaliacao).label("media_aval"),
            func.count(AvaliacaoPedido.id_avaliacao).label("total_aval"),
        )
        .join(Pedido, AvaliacaoPedido.id_pedido == Pedido.id_pedido)
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .group_by(ItemPedido.id_produto)
        .subquery()
    )

    # ── Subquery: total de vendas e preço médio por produto ─────────────────
    vendas_sub = (
        select(
            ItemPedido.id_produto.label("id_produto"),
            func.count(ItemPedido.id_item).label("total_vendas"),
            func.avg(ItemPedido.preco_BRL).label("preco_medio"),
        )
        .group_by(ItemPedido.id_produto)
        .subquery()
    )

    # ── Query base com stats ─────────────────────────────────────────────────
    base = (
        select(
            Produto,
            aval_sub.c.media_aval,
            aval_sub.c.total_aval,
            vendas_sub.c.total_vendas,
            vendas_sub.c.preco_medio,
        )
        .outerjoin(aval_sub, aval_sub.c.id_produto == Produto.id_produto)
        .outerjoin(vendas_sub, vendas_sub.c.id_produto == Produto.id_produto)
    )

    if search:
        termo = f"%{search.lower()}%"
        base = base.where(
            func.lower(Produto.nome_produto).like(termo)
            | func.lower(Produto.categoria_produto).like(termo)
        )

    if categoria:
        cats = [c.strip() for c in categoria.split(",") if c.strip()]
        if len(cats) == 1:
            base = base.where(Produto.categoria_produto == cats[0])
        elif cats:
            base = base.where(Produto.categoria_produto.in_(cats))

    total = db.scalar(select(func.count()).select_from(base.subquery()))
    pages = math.ceil(total / page_size) if total else 1

    # ── Ordenação ────────────────────────────────────────────────────────────
    if ordenar == "avaliacao":
        order_clause = [
            nulls_last(aval_sub.c.media_aval.desc()),
            nulls_last(aval_sub.c.total_aval.desc()),
            Produto.nome_produto,
        ]
    elif ordenar == "vendas":
        order_clause = [
            nulls_last(vendas_sub.c.total_vendas.desc()),
            Produto.nome_produto,
        ]
    elif ordenar == "preco_asc":
        order_clause = [
            nulls_last(vendas_sub.c.preco_medio.asc()),
            Produto.nome_produto,
        ]
    elif ordenar == "preco_desc":
        order_clause = [
            nulls_last(vendas_sub.c.preco_medio.desc()),
            Produto.nome_produto,
        ]
    else:
        order_clause = [Produto.nome_produto]

    rows = db.execute(
        base.order_by(*order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        ProdutoResponse(
            id_produto=r.Produto.id_produto,
            nome_produto=r.Produto.nome_produto,
            categoria_produto=r.Produto.categoria_produto,
            peso_produto_gramas=r.Produto.peso_produto_gramas,
            comprimento_centimetros=r.Produto.comprimento_centimetros,
            altura_centimetros=r.Produto.altura_centimetros,
            largura_centimetros=r.Produto.largura_centimetros,
            media_avaliacao=round(float(r.media_aval), 2) if r.media_aval else None,
            total_avaliacoes=r.total_aval or 0,
            total_vendas=r.total_vendas or 0,
            preco_medio=round(float(r.preco_medio), 2) if r.preco_medio else None,
        )
        for r in rows
    ]

    return PaginatedProdutos(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/categorias", response_model=List[CategoriaResponse], summary="Listar categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """Retorna todas as categorias com o total de produtos em cada uma."""
    rows = db.execute(
        select(Produto.categoria_produto, func.count(Produto.id_produto).label("total"))
        .group_by(Produto.categoria_produto)
        .order_by(Produto.categoria_produto)
    ).all()
    return [CategoriaResponse(categoria=r[0], total_produtos=r[1]) for r in rows]


@router.get("/{id_produto}", response_model=ProdutoDetalhe, summary="Detalhes do produto")
def obter_produto(id_produto: str, db: Session = Depends(get_db)):
    """Retorna detalhes completos de um produto, incluindo estatísticas de vendas e avaliações."""
    produto = _get_produto_or_404(id_produto, db)
    stats = _stats_para_produto(id_produto, db)
    return ProdutoDetalhe(
        id_produto=produto.id_produto,
        nome_produto=produto.nome_produto,
        categoria_produto=produto.categoria_produto,
        peso_produto_gramas=produto.peso_produto_gramas,
        comprimento_centimetros=produto.comprimento_centimetros,
        altura_centimetros=produto.altura_centimetros,
        largura_centimetros=produto.largura_centimetros,
        **stats,
    )


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED, summary="Criar produto")
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto no sistema."""
    novo = Produto(
        id_produto=uuid.uuid4().hex,
        **payload.model_dump(),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{id_produto}", response_model=ProdutoResponse, summary="Atualizar produto")
def atualizar_produto(
    id_produto: str, payload: ProdutoUpdate, db: Session = Depends(get_db)
):
    """Atualiza os dados de um produto existente (campos opcionais)."""
    produto = _get_produto_or_404(id_produto, db)
    dados = payload.model_dump(exclude_unset=True)
    for campo, valor in dados.items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover produto")
def deletar_produto(id_produto: str, db: Session = Depends(get_db)):
    """Remove um produto do sistema."""
    produto = _get_produto_or_404(id_produto, db)
    db.delete(produto)
    db.commit()


@router.get(
    "/{id_produto}/avaliacoes",
    response_model=PaginatedAvaliacoes,
    summary="Avaliações do produto",
)
def listar_avaliacoes(
    id_produto: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Lista as avaliações de um produto com paginação e média."""
    _get_produto_or_404(id_produto, db)

    base_query = (
        select(AvaliacaoPedido)
        .join(Pedido, AvaliacaoPedido.id_pedido == Pedido.id_pedido)
        .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
        .where(ItemPedido.id_produto == id_produto)
        .distinct()
    )

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))
    pages = math.ceil(total / page_size) if total else 1

    items = db.scalars(
        base_query.order_by(AvaliacaoPedido.data_comentario.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    media = None
    if total:
        media_raw = db.scalar(
            select(func.avg(AvaliacaoPedido.avaliacao))
            .join(Pedido, AvaliacaoPedido.id_pedido == Pedido.id_pedido)
            .join(ItemPedido, ItemPedido.id_pedido == Pedido.id_pedido)
            .where(ItemPedido.id_produto == id_produto)
        )
        if media_raw:
            media = round(float(media_raw), 2)

    return PaginatedAvaliacoes(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        media_avaliacao=media,
    )
