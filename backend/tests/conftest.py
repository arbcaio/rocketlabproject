"""
Fixtures compartilhados entre todos os testes.

Estratégia de isolamento:
- Um banco SQLite em memória com StaticPool por função de teste.
- StaticPool garante que todos os objetos de conexão usem o mesmo
  canal subjacente, logo a sessão de seed e a sessão do endpoint
  enxergam os mesmos dados.
- As tabelas são criadas antes e destruídas após cada teste.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importar todos os modelos para registrá-los no Base antes do create_all
from app.database import Base, get_db
from app.main import app
from app.models import (  # noqa: F401  – imports necessários para o Base
    consumidor,
    vendedor,
    produto,
    pedido,
    item_pedido,
    avaliacao_pedido,
)

SQLITE_URL = "sqlite:///:memory:"


# ── Fixtures de infraestrutura ────────────────────────────────────────────────

@pytest.fixture()
def engine():
    """Engine SQLite in-memory com pool estático (conexão única compartilhada)."""
    eng = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def db(engine):
    """Sessão direta para inserir dados de teste."""
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(engine):
    """TestClient com override do get_db apontando para o banco de teste."""
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        s = Session()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers de seed ───────────────────────────────────────────────────────────

from app.models.consumidor import Consumidor
from app.models.vendedor import Vendedor
from app.models.produto import Produto
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.avaliacao_pedido import AvaliacaoPedido


def make_consumidor(db, id="cons01", nome="Consumidor Teste", cidade="SP", estado="SP"):
    c = Consumidor(
        id_consumidor=id,
        prefixo_cep="01000",
        nome_consumidor=nome,
        cidade=cidade,
        estado=estado,
    )
    db.add(c)
    db.commit()
    return c


def make_vendedor(db, id="vend01", nome="Vendedor Teste", cidade="RJ", estado="RJ"):
    v = Vendedor(
        id_vendedor=id,
        nome_vendedor=nome,
        prefixo_cep="20000",
        cidade=cidade,
        estado=estado,
    )
    db.add(v)
    db.commit()
    return v


def make_produto(
    db,
    id="prod01",
    nome="Produto Teste",
    categoria="eletronicos",
    peso=500.0,
    comprimento=20.0,
    altura=10.0,
    largura=5.0,
):
    p = Produto(
        id_produto=id,
        nome_produto=nome,
        categoria_produto=categoria,
        peso_produto_gramas=peso,
        comprimento_centimetros=comprimento,
        altura_centimetros=altura,
        largura_centimetros=largura,
    )
    db.add(p)
    db.commit()
    return p


def make_pedido(db, id="ped01", id_consumidor="cons01", status="entregue"):
    p = Pedido(
        id_pedido=id,
        id_consumidor=id_consumidor,
        status=status,
    )
    db.add(p)
    db.commit()
    return p


def make_item_pedido(
    db,
    id_pedido="ped01",
    id_item=1,
    id_produto="prod01",
    id_vendedor="vend01",
    preco=99.90,
    frete=10.0,
):
    i = ItemPedido(
        id_pedido=id_pedido,
        id_item=id_item,
        id_produto=id_produto,
        id_vendedor=id_vendedor,
        preco_BRL=preco,
        preco_frete=frete,
    )
    db.add(i)
    db.commit()
    return i


def make_avaliacao(
    db,
    id="aval01",
    id_pedido="ped01",
    nota=5,
    titulo="Ótimo",
    comentario="Recomendo",
):
    a = AvaliacaoPedido(
        id_avaliacao=id,
        id_pedido=id_pedido,
        avaliacao=nota,
        titulo_comentario=titulo,
        comentario=comentario,
    )
    db.add(a)
    db.commit()
    return a
