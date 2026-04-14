"""
Testes de integração — endpoints de Vendedores.

Cobertura:
  GET    /vendedores                    – listagem, busca, filtro, paginação
  GET    /vendedores/{id}               – detalhe
  POST   /vendedores                    – criação com validação
  PUT    /vendedores/{id}               – atualização parcial
  DELETE /vendedores/{id}               – remoção
  GET    /vendedores/{id}/produtos      – produtos distintos vendidos pelo vendedor
"""

from tests.conftest import (
    make_consumidor,
    make_item_pedido,
    make_pedido,
    make_produto,
    make_vendedor,
)

_PAYLOAD = {
    "nome_vendedor": "Loja Exemplo",
    "prefixo_cep": "20040",
    "cidade": "Rio de Janeiro",
    "estado": "RJ",
}


# ══════════════════════════════════════════════════════════════════════════════
# GET /vendedores
# ══════════════════════════════════════════════════════════════════════════════

class TestListarVendedores:

    def test_lista_vazia(self, client):
        resp = client.get("/vendedores")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["pages"] == 1

    def test_retorna_vendedor_criado(self, client, db):
        make_vendedor(db, id="v1", nome="Mega Loja", cidade="Curitiba", estado="PR")
        body = client.get("/vendedores").json()
        assert body["total"] == 1
        item = body["items"][0]
        assert item["id_vendedor"] == "v1"
        assert item["nome_vendedor"] == "Mega Loja"
        assert item["estado"] == "PR"

    def test_busca_por_nome(self, client, db):
        make_vendedor(db, id="v1", nome="Tech Store", cidade="SP", estado="SP")
        make_vendedor(db, id="v2", nome="Livros & Cia", cidade="RJ", estado="RJ")
        body = client.get("/vendedores?search=tech").json()
        assert body["total"] == 1
        assert body["items"][0]["nome_vendedor"] == "Tech Store"

    def test_busca_por_cidade(self, client, db):
        make_vendedor(db, id="v1", nome="Loja A", cidade="Manaus", estado="AM")
        make_vendedor(db, id="v2", nome="Loja B", cidade="Belém", estado="PA")
        body = client.get("/vendedores?search=manaus").json()
        assert body["total"] == 1

    def test_busca_case_insensitive(self, client, db):
        make_vendedor(db, id="v1", nome="Eletro Total", cidade="X", estado="SP")
        assert client.get("/vendedores?search=ELETRO").json()["total"] == 1

    def test_filtro_por_estado(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="SP", estado="SP")
        make_vendedor(db, id="v2", nome="B", cidade="RJ", estado="RJ")
        make_vendedor(db, id="v3", nome="C", cidade="SP2", estado="SP")
        body = client.get("/vendedores?estado=SP").json()
        assert body["total"] == 2

    def test_filtro_estado_case_insensitive(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="MG")
        assert client.get("/vendedores?estado=mg").json()["total"] == 1

    def test_paginacao(self, client, db):
        for i in range(5):
            make_vendedor(db, id=f"v{i}", nome=f"Vendedor {i}", cidade="X", estado="SP")
        body = client.get("/vendedores?page=1&page_size=2").json()
        assert body["total"] == 5
        assert body["pages"] == 3
        assert len(body["items"]) == 2

    def test_page_invalida_retorna_422(self, client):
        assert client.get("/vendedores?page=0").status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# GET /vendedores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDetalharVendedor:

    def test_404_para_id_inexistente(self, client):
        assert client.get("/vendedores/nao-existe").status_code == 404

    def test_retorna_dados_corretos(self, client, db):
        make_vendedor(db, id="v1", nome="Super Loja", cidade="Florianópolis", estado="SC")
        body = client.get("/vendedores/v1").json()
        assert body["id_vendedor"] == "v1"
        assert body["nome_vendedor"] == "Super Loja"
        assert body["cidade"] == "Florianópolis"
        assert body["estado"] == "SC"


# ══════════════════════════════════════════════════════════════════════════════
# POST /vendedores
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarVendedor:

    def test_cria_vendedor_completo(self, client):
        resp = client.post("/vendedores", json=_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["nome_vendedor"] == "Loja Exemplo"
        assert body["estado"] == "RJ"
        assert len(body["id_vendedor"]) == 32

    def test_nome_vazio_retorna_422(self, client):
        assert client.post("/vendedores", json={**_PAYLOAD, "nome_vendedor": ""}).status_code == 422

    def test_estado_invalido_retorna_422(self, client):
        assert client.post("/vendedores", json={**_PAYLOAD, "estado": "X"}).status_code == 422

    def test_campos_obrigatorios_ausentes_retorna_422(self, client):
        assert client.post("/vendedores", json={}).status_code == 422

    def test_ids_gerados_sao_unicos(self, client):
        ids = {
            client.post("/vendedores", json={**_PAYLOAD, "nome_vendedor": f"V{i}"}).json()["id_vendedor"]
            for i in range(5)
        }
        assert len(ids) == 5


# ══════════════════════════════════════════════════════════════════════════════
# PUT /vendedores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestAtualizarVendedor:

    def test_atualiza_nome(self, client, db):
        make_vendedor(db, id="v1", nome="Nome Antigo", cidade="X", estado="SP")
        resp = client.put("/vendedores/v1", json={"nome_vendedor": "Nome Novo"})
        assert resp.status_code == 200
        assert resp.json()["nome_vendedor"] == "Nome Novo"

    def test_partial_update_preserva_campos(self, client, db):
        make_vendedor(db, id="v1", nome="Loja X", cidade="Goiânia", estado="GO")
        body = client.put("/vendedores/v1", json={"nome_vendedor": "Loja Y"}).json()
        assert body["nome_vendedor"] == "Loja Y"
        assert body["cidade"] == "Goiânia"  # inalterado

    def test_persistencia(self, client, db):
        make_vendedor(db, id="v1", nome="Antigo", cidade="X", estado="SP")
        client.put("/vendedores/v1", json={"nome_vendedor": "Persistido"})
        assert client.get("/vendedores/v1").json()["nome_vendedor"] == "Persistido"

    def test_404_para_id_inexistente(self, client):
        assert client.put("/vendedores/nao-existe", json={"nome_vendedor": "X"}).status_code == 404

    def test_estado_invalido_retorna_422(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="SP")
        assert client.put("/vendedores/v1", json={"estado": "S"}).status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /vendedores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDeletarVendedor:

    def test_retorna_204(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="SP")
        assert client.delete("/vendedores/v1").status_code == 204

    def test_404_apos_delecao(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="SP")
        client.delete("/vendedores/v1")
        assert client.get("/vendedores/v1").status_code == 404

    def test_some_da_listagem(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="SP")
        client.delete("/vendedores/v1")
        assert client.get("/vendedores").json()["total"] == 0

    def test_404_para_id_inexistente(self, client):
        assert client.delete("/vendedores/nao-existe").status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# GET /vendedores/{id}/produtos
# ══════════════════════════════════════════════════════════════════════════════

class TestProdutosVendedor:

    def _seed(self, db):
        """Cria consumidor, vendedor e produto base."""
        make_consumidor(db)
        make_vendedor(db)
        make_produto(db)

    def test_404_vendedor_inexistente(self, client):
        assert client.get("/vendedores/nao-existe/produtos").status_code == 404

    def test_sem_vendas_retorna_vazio(self, client, db):
        make_vendedor(db, id="v1", nome="A", cidade="X", estado="SP")
        body = client.get("/vendedores/v1/produtos").json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_retorna_produto_vendido(self, client, db):
        self._seed(db)
        make_pedido(db)
        make_item_pedido(db)  # associa prod01 ao vend01
        body = client.get("/vendedores/vend01/produtos").json()
        assert body["total"] == 1
        assert body["items"][0]["id_produto"] == "prod01"

    def test_produto_aparece_uma_vez_mesmo_com_multiplas_vendas(self, client, db):
        """Mesmo produto vendido em pedidos diferentes deve aparecer só uma vez."""
        self._seed(db)
        make_pedido(db, id="ped1")
        make_item_pedido(db, id_pedido="ped1", id_item=1)
        make_pedido(db, id="ped2")
        make_item_pedido(db, id_pedido="ped2", id_item=1)
        body = client.get("/vendedores/vend01/produtos").json()
        assert body["total"] == 1

    def test_nao_retorna_produtos_de_outro_vendedor(self, client, db):
        make_consumidor(db)
        make_vendedor(db, id="v1")
        make_vendedor(db, id="v2", nome="Outro", cidade="X", estado="RJ")
        make_produto(db, id="p1")
        make_produto(db, id="p2", nome="Produto B", categoria="livros")
        make_pedido(db, id="ped1")
        make_item_pedido(db, id_pedido="ped1", id_produto="p1", id_vendedor="v1", id_item=1)
        make_pedido(db, id="ped2")
        make_item_pedido(db, id_pedido="ped2", id_produto="p2", id_vendedor="v2", id_item=1)
        body = client.get("/vendedores/v1/produtos").json()
        assert body["total"] == 1
        assert body["items"][0]["id_produto"] == "p1"
