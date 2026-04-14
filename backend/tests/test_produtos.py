"""
Testes de integração — endpoints de Produtos.

Cobertura:
  GET  /produtos               – listagem, busca, filtro, ordenação, paginação, stats
  GET  /produtos/categorias    – lista de categorias com contagem
  GET  /produtos/{id}          – detalhe com stats
  POST /produtos               – criação com validação
  PUT  /produtos/{id}          – atualização parcial
  DELETE /produtos/{id}        – remoção
  GET  /produtos/{id}/avaliacoes – avaliações paginadas com média
"""

from tests.conftest import (
    make_avaliacao,
    make_consumidor,
    make_item_pedido,
    make_pedido,
    make_produto,
    make_vendedor,
)


# ── Helpers de cenário ────────────────────────────────────────────────────────

def _seed_infra(db):
    """Cria consumidor e vendedor base para testes que precisam de pedidos."""
    make_consumidor(db)
    make_vendedor(db)


def _seed_pedido_com_venda(db, id_pedido, id_produto, preco, id_item=1):
    make_pedido(db, id=id_pedido)
    make_item_pedido(db, id_pedido=id_pedido, id_produto=id_produto,
                     id_item=id_item, preco=preco)


def _seed_pedido_com_avaliacao(db, id_pedido, id_produto, preco, id_avaliacao, nota):
    _seed_pedido_com_venda(db, id_pedido, id_produto, preco)
    make_avaliacao(db, id=id_avaliacao, id_pedido=id_pedido, nota=nota)


# ══════════════════════════════════════════════════════════════════════════════
# GET /produtos
# ══════════════════════════════════════════════════════════════════════════════

class TestListarProdutos:

    def test_lista_vazia(self, client):
        resp = client.get("/produtos")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["pages"] == 1

    def test_retorna_produto_criado(self, client, db):
        make_produto(db, id="p1", nome="Notebook Pro", categoria="informatica")
        resp = client.get("/produtos")
        body = resp.json()
        assert body["total"] == 1
        item = body["items"][0]
        assert item["id_produto"] == "p1"
        assert item["nome_produto"] == "Notebook Pro"
        assert item["categoria_produto"] == "informatica"

    def test_stats_zerados_sem_vendas(self, client, db):
        make_produto(db, id="p1", nome="Produto Sem Venda", categoria="teste")
        item = client.get("/produtos").json()["items"][0]
        assert item["total_vendas"] == 0
        assert item["total_avaliacoes"] == 0
        assert item["media_avaliacao"] is None
        assert item["preco_medio"] is None

    def test_stats_com_venda_e_avaliacao(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Produto Com Dados", categoria="eletronicos")
        _seed_pedido_com_avaliacao(db, "ped1", "p1", 200.00, "av1", nota=4)

        item = client.get("/produtos").json()["items"][0]
        assert item["total_vendas"] == 1
        assert item["total_avaliacoes"] == 1
        assert item["media_avaliacao"] == 4.0
        assert item["preco_medio"] == 200.0

    def test_busca_por_nome(self, client, db):
        make_produto(db, id="p1", nome="Teclado Mecânico", categoria="perifericos")
        make_produto(db, id="p2", nome="Mouse Gamer", categoria="perifericos")
        resp = client.get("/produtos?search=teclado")
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["nome_produto"] == "Teclado Mecânico"

    def test_busca_por_categoria(self, client, db):
        """Busca também encontra termos que aparecem na categoria."""
        make_produto(db, id="p1", nome="Produto A", categoria="eletronicos")
        make_produto(db, id="p2", nome="Produto B", categoria="livros")
        assert client.get("/produtos?search=eletronicos").json()["total"] == 1

    def test_busca_case_insensitive(self, client, db):
        make_produto(db, id="p1", nome="Notebook Dell", categoria="informatica")
        assert client.get("/produtos?search=NOTEBOOK").json()["total"] == 1

    def test_busca_sem_resultado(self, client, db):
        make_produto(db, id="p1", nome="Notebook", categoria="informatica")
        assert client.get("/produtos?search=televisao").json()["total"] == 0

    def test_filtro_categoria_unica(self, client, db):
        make_produto(db, id="p1", nome="Produto A", categoria="livros")
        make_produto(db, id="p2", nome="Produto B", categoria="eletronicos")
        resp = client.get("/produtos?categoria=livros")
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["categoria_produto"] == "livros"

    def test_filtro_multiplas_categorias(self, client, db):
        make_produto(db, id="p1", nome="Produto A", categoria="livros")
        make_produto(db, id="p2", nome="Produto B", categoria="eletronicos")
        make_produto(db, id="p3", nome="Produto C", categoria="esportes")
        resp = client.get("/produtos?categoria=livros,eletronicos")
        body = resp.json()
        assert body["total"] == 2
        cats = {i["categoria_produto"] for i in body["items"]}
        assert cats == {"livros", "eletronicos"}

    def test_filtro_categoria_inexistente_retorna_vazio(self, client, db):
        make_produto(db, id="p1", nome="Produto A", categoria="livros")
        assert client.get("/produtos?categoria=nao_existe").json()["total"] == 0

    # ── Ordenação ──────────────────────────────────────────────────────────

    def test_ordenacao_padrao_por_nome(self, client, db):
        make_produto(db, id="p1", nome="Zebra", categoria="x")
        make_produto(db, id="p2", nome="Abacate", categoria="x")
        nomes = [i["nome_produto"] for i in client.get("/produtos").json()["items"]]
        assert nomes == ["Abacate", "Zebra"]

    def test_ordenacao_por_avaliacao(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Fraco", categoria="x")
        make_produto(db, id="p2", nome="Excelente", categoria="x")
        _seed_pedido_com_avaliacao(db, "ped1", "p1", 50.0, "av1", nota=2)
        _seed_pedido_com_avaliacao(db, "ped2", "p2", 50.0, "av2", nota=5)

        nomes = [
            i["nome_produto"]
            for i in client.get("/produtos?ordenar=avaliacao").json()["items"]
        ]
        assert nomes[0] == "Excelente"
        assert nomes[1] == "Fraco"

    def test_ordenacao_por_vendas(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Pouco Vendido", categoria="x")
        make_produto(db, id="p2", nome="Mais Vendido", categoria="x")
        _seed_pedido_com_venda(db, "ped1", "p1", 50.0, id_item=1)
        _seed_pedido_com_venda(db, "ped2", "p2", 50.0, id_item=1)
        _seed_pedido_com_venda(db, "ped3", "p2", 50.0, id_item=2)

        nomes = [
            i["nome_produto"]
            for i in client.get("/produtos?ordenar=vendas").json()["items"]
        ]
        assert nomes[0] == "Mais Vendido"

    def test_ordenacao_preco_asc(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Caro", categoria="x")
        make_produto(db, id="p2", nome="Barato", categoria="x")
        _seed_pedido_com_venda(db, "ped1", "p1", 500.0)
        _seed_pedido_com_venda(db, "ped2", "p2", 50.0)

        nomes = [
            i["nome_produto"]
            for i in client.get("/produtos?ordenar=preco_asc").json()["items"]
        ]
        assert nomes == ["Barato", "Caro"]

    def test_ordenacao_preco_desc(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Caro", categoria="x")
        make_produto(db, id="p2", nome="Barato", categoria="x")
        _seed_pedido_com_venda(db, "ped1", "p1", 500.0)
        _seed_pedido_com_venda(db, "ped2", "p2", 50.0)

        nomes = [
            i["nome_produto"]
            for i in client.get("/produtos?ordenar=preco_desc").json()["items"]
        ]
        assert nomes == ["Caro", "Barato"]

    def test_sem_vendas_fica_no_final_na_ordenacao_preco(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Com Preço", categoria="x")
        make_produto(db, id="p2", nome="Sem Preço", categoria="x")
        _seed_pedido_com_venda(db, "ped1", "p1", 100.0)

        nomes = [
            i["nome_produto"]
            for i in client.get("/produtos?ordenar=preco_asc").json()["items"]
        ]
        assert nomes[-1] == "Sem Preço"

    # ── Paginação ──────────────────────────────────────────────────────────

    def test_paginacao_page_size(self, client, db):
        for i in range(5):
            make_produto(db, id=f"p{i}", nome=f"Produto {i}", categoria="x")
        resp = client.get("/produtos?page=1&page_size=2")
        body = resp.json()
        assert body["total"] == 5
        assert body["pages"] == 3
        assert len(body["items"]) == 2

    def test_paginacao_segunda_pagina(self, client, db):
        for i in range(4):
            make_produto(db, id=f"p{i}", nome=f"Produto {i}", categoria="x")
        resp = client.get("/produtos?page=2&page_size=2")
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["page"] == 2

    def test_page_invalida_retorna_422(self, client):
        resp = client.get("/produtos?page=0")
        assert resp.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# GET /produtos/categorias
# ══════════════════════════════════════════════════════════════════════════════

class TestCategorias:

    def test_lista_vazia(self, client):
        resp = client.get("/produtos/categorias")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_retorna_categorias_com_contagem(self, client, db):
        make_produto(db, id="p1", nome="A", categoria="livros")
        make_produto(db, id="p2", nome="B", categoria="livros")
        make_produto(db, id="p3", nome="C", categoria="eletronicos")
        resp = client.get("/produtos/categorias")
        totais = {c["categoria"]: c["total_produtos"] for c in resp.json()}
        assert totais["livros"] == 2
        assert totais["eletronicos"] == 1

    def test_resultado_ordenado_por_categoria(self, client, db):
        make_produto(db, id="p1", nome="A", categoria="zebra")
        make_produto(db, id="p2", nome="B", categoria="abacate")
        cats = [c["categoria"] for c in client.get("/produtos/categorias").json()]
        assert cats == sorted(cats)


# ══════════════════════════════════════════════════════════════════════════════
# GET /produtos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDetalharProduto:

    def test_404_para_id_inexistente(self, client):
        assert client.get("/produtos/nao-existe").status_code == 404

    def test_retorna_produto_sem_stats(self, client, db):
        make_produto(db, id="p1", nome="Monitor 24", categoria="eletronicos",
                     peso=3000, comprimento=57, altura=37, largura=8)
        resp = client.get("/produtos/p1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id_produto"] == "p1"
        assert body["nome_produto"] == "Monitor 24"
        assert body["total_vendas"] == 0
        assert body["total_avaliacoes"] == 0
        assert body["media_avaliacao"] is None
        assert body["receita_total"] == 0.0

    def test_retorna_stats_corretas(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="HD Externo", categoria="informatica")
        _seed_pedido_com_avaliacao(db, "ped1", "p1", 250.00, "av1", nota=4)
        _seed_pedido_com_avaliacao(db, "ped2", "p1", 270.00, "av2", nota=5)

        body = client.get("/produtos/p1").json()
        assert body["total_vendas"] == 2
        assert body["receita_total"] == 520.0
        assert body["preco_medio"] == 260.0
        assert body["total_avaliacoes"] == 2
        assert body["media_avaliacao"] == 4.5

    def test_campos_opcionais_nulos(self, client, db):
        make_produto(db, id="p1", nome="Item", categoria="x",
                     peso=None, comprimento=None, altura=None, largura=None)
        body = client.get("/produtos/p1").json()
        assert body["peso_produto_gramas"] is None
        assert body["comprimento_centimetros"] is None


# ══════════════════════════════════════════════════════════════════════════════
# POST /produtos
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarProduto:

    def test_cria_produto_completo(self, client):
        payload = {
            "nome_produto": "Cadeira Gamer",
            "categoria_produto": "moveis",
            "peso_produto_gramas": 15000,
            "comprimento_centimetros": 70,
            "altura_centimetros": 130,
            "largura_centimetros": 65,
        }
        resp = client.post("/produtos", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["nome_produto"] == "Cadeira Gamer"
        assert body["categoria_produto"] == "moveis"
        assert len(body["id_produto"]) == 32  # uuid4().hex

    def test_cria_produto_minimo(self, client):
        resp = client.post("/produtos", json={
            "nome_produto": "Item Simples",
            "categoria_produto": "geral",
        })
        assert resp.status_code == 201
        assert resp.json()["peso_produto_gramas"] is None

    def test_produto_aparece_na_listagem_apos_criacao(self, client):
        client.post("/produtos", json={
            "nome_produto": "Produto Novo",
            "categoria_produto": "geral",
        })
        assert client.get("/produtos").json()["total"] == 1

    def test_nome_vazio_retorna_422(self, client):
        resp = client.post("/produtos", json={
            "nome_produto": "",
            "categoria_produto": "geral",
        })
        assert resp.status_code == 422

    def test_categoria_vazia_retorna_422(self, client):
        resp = client.post("/produtos", json={
            "nome_produto": "Produto X",
            "categoria_produto": "",
        })
        assert resp.status_code == 422

    def test_peso_negativo_retorna_422(self, client):
        resp = client.post("/produtos", json={
            "nome_produto": "Produto X",
            "categoria_produto": "geral",
            "peso_produto_gramas": -10,
        })
        assert resp.status_code == 422

    def test_campos_obrigatorios_ausentes_retorna_422(self, client):
        assert client.post("/produtos", json={"nome_produto": "X"}).status_code == 422
        assert client.post("/produtos", json={}).status_code == 422

    def test_ids_gerados_sao_unicos(self, client):
        ids = {
            client.post("/produtos", json={
                "nome_produto": f"P{i}", "categoria_produto": "x"
            }).json()["id_produto"]
            for i in range(5)
        }
        assert len(ids) == 5


# ══════════════════════════════════════════════════════════════════════════════
# PUT /produtos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestAtualizarProduto:

    def test_atualiza_nome(self, client, db):
        make_produto(db, id="p1", nome="Nome Antigo", categoria="x")
        resp = client.put("/produtos/p1", json={"nome_produto": "Nome Novo"})
        assert resp.status_code == 200
        assert resp.json()["nome_produto"] == "Nome Novo"

    def test_atualiza_categoria(self, client, db):
        make_produto(db, id="p1", nome="Prod", categoria="categoria_antiga")
        resp = client.put("/produtos/p1", json={"categoria_produto": "categoria_nova"})
        assert resp.status_code == 200
        assert resp.json()["categoria_produto"] == "categoria_nova"

    def test_atualiza_apenas_campo_enviado(self, client, db):
        """Campos não enviados não devem ser alterados (partial update)."""
        make_produto(db, id="p1", nome="Produto Original", categoria="original")
        body = client.put("/produtos/p1", json={"nome_produto": "Novo Nome"}).json()
        assert body["nome_produto"] == "Novo Nome"
        assert body["categoria_produto"] == "original"  # inalterado

    def test_alteracao_persistida(self, client, db):
        make_produto(db, id="p1", nome="Antigo", categoria="x")
        client.put("/produtos/p1", json={"nome_produto": "Persistido"})
        assert client.get("/produtos/p1").json()["nome_produto"] == "Persistido"

    def test_404_para_id_inexistente(self, client):
        resp = client.put("/produtos/nao-existe", json={"nome_produto": "X"})
        assert resp.status_code == 404

    def test_peso_negativo_retorna_422(self, client, db):
        make_produto(db, id="p1", nome="Prod", categoria="x")
        resp = client.put("/produtos/p1", json={"peso_produto_gramas": -5})
        assert resp.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /produtos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDeletarProduto:

    def test_retorna_204(self, client, db):
        make_produto(db, id="p1", nome="A Deletar", categoria="x")
        assert client.delete("/produtos/p1").status_code == 204

    def test_produto_nao_existe_apos_delecao(self, client, db):
        make_produto(db, id="p1", nome="A Deletar", categoria="x")
        client.delete("/produtos/p1")
        assert client.get("/produtos/p1").status_code == 404

    def test_produto_some_da_listagem(self, client, db):
        make_produto(db, id="p1", nome="A Deletar", categoria="x")
        client.delete("/produtos/p1")
        assert client.get("/produtos").json()["total"] == 0

    def test_404_para_id_inexistente(self, client):
        assert client.delete("/produtos/nao-existe").status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# GET /produtos/{id}/avaliacoes
# ══════════════════════════════════════════════════════════════════════════════

class TestAvaliacoes:

    def test_404_para_produto_inexistente(self, client):
        assert client.get("/produtos/nao-existe/avaliacoes").status_code == 404

    def test_sem_avaliacoes(self, client, db):
        make_produto(db, id="p1", nome="Sem Aval", categoria="x")
        resp = client.get("/produtos/p1/avaliacoes")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["media_avaliacao"] is None

    def test_retorna_avaliacoes_com_dados(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Produto", categoria="x")
        _seed_pedido_com_avaliacao(db, "ped1", "p1", 100.0, "av1", nota=4)

        resp = client.get("/produtos/p1/avaliacoes")
        body = resp.json()
        assert body["total"] == 1
        assert body["media_avaliacao"] == 4.0
        aval = body["items"][0]
        assert aval["avaliacao"] == 4
        assert aval["titulo_comentario"] == "Ótimo"

    def test_media_calculada_corretamente(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Produto", categoria="x")
        _seed_pedido_com_avaliacao(db, "ped1", "p1", 50.0, "av1", nota=5)
        _seed_pedido_com_avaliacao(db, "ped2", "p1", 50.0, "av2", nota=3)
        _seed_pedido_com_avaliacao(db, "ped3", "p1", 50.0, "av3", nota=4)

        media = client.get("/produtos/p1/avaliacoes").json()["media_avaliacao"]
        assert media == 4.0  # (5+3+4) / 3

    def test_paginacao_avaliacoes(self, client, db):
        _seed_infra(db)
        make_produto(db, id="p1", nome="Produto", categoria="x")
        for i in range(5):
            _seed_pedido_com_avaliacao(db, f"ped{i}", "p1", 10.0, f"av{i}", nota=3)

        resp = client.get("/produtos/p1/avaliacoes?page=1&page_size=2")
        body = resp.json()
        assert body["total"] == 5
        assert body["pages"] == 3
        assert len(body["items"]) == 2

    def test_page_invalida_retorna_422(self, client, db):
        make_produto(db, id="p1", nome="Produto", categoria="x")
        assert client.get("/produtos/p1/avaliacoes?page=0").status_code == 422
