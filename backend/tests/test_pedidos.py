"""
Testes de integração — endpoints de Pedidos.

Cobertura:
  GET    /pedidos                       – listagem, filtro por status/consumidor, paginação
  GET    /pedidos/{id}                  – detalhe com itens, valor_total, avaliação
  POST   /pedidos                       – criação com itens e validações
  PUT    /pedidos/{id}                  – atualização de status
  DELETE /pedidos/{id}                  – remoção
  POST   /pedidos/{id}/avaliacao        – criar avaliação (1 por pedido, nota 1–5)
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

def _infra(db):
    """Cria consumidor e vendedor padrão (necessários para FK dos itens)."""
    make_consumidor(db)  # id=cons01
    make_vendedor(db)    # id=vend01


def _payload_pedido(id_consumidor="cons01"):
    return {
        "id_consumidor": id_consumidor,
        "status": "pendente",
        "itens": [
            {"id_produto": "prod01", "id_vendedor": "vend01", "preco_BRL": 100.0, "preco_frete": 10.0}
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════
# GET /pedidos
# ══════════════════════════════════════════════════════════════════════════════

class TestListarPedidos:

    def test_lista_vazia(self, client):
        resp = client.get("/pedidos")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["pages"] == 1

    def test_retorna_pedido_criado(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        body = client.get("/pedidos").json()
        assert body["total"] == 1
        assert body["items"][0]["id_pedido"] == "ped1"
        assert body["items"][0]["status"] == "entregue"

    def test_filtro_por_status(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        make_pedido(db, id="ped2", id_consumidor="cons01", status="pendente")
        body = client.get("/pedidos?status=entregue").json()
        assert body["total"] == 1
        assert body["items"][0]["status"] == "entregue"

    def test_filtro_por_consumidor(self, client, db):
        make_consumidor(db, id="c1")
        make_consumidor(db, id="c2", nome="Outro", cidade="RJ", estado="RJ")
        make_pedido(db, id="ped1", id_consumidor="c1")
        make_pedido(db, id="ped2", id_consumidor="c2")
        body = client.get("/pedidos?id_consumidor=c1").json()
        assert body["total"] == 1
        assert body["items"][0]["id_consumidor"] == "c1"

    def test_paginacao(self, client, db):
        make_consumidor(db)
        for i in range(5):
            make_pedido(db, id=f"ped{i}", id_consumidor="cons01")
        body = client.get("/pedidos?page=1&page_size=2").json()
        assert body["total"] == 5
        assert body["pages"] == 3
        assert len(body["items"]) == 2

    def test_page_invalida_retorna_422(self, client):
        assert client.get("/pedidos?page=0").status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# GET /pedidos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDetalharPedido:

    def test_404_para_id_inexistente(self, client):
        assert client.get("/pedidos/nao-existe").status_code == 404

    def test_retorna_pedido_sem_itens(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="pendente")
        body = client.get("/pedidos/ped1").json()
        assert body["id_pedido"] == "ped1"
        assert body["status"] == "pendente"
        assert body["itens"] == []
        assert body["total_itens"] == 0
        assert body["valor_total"] == 0.0
        assert body["avaliacao"] is None

    def test_retorna_pedido_com_itens(self, client, db):
        _infra(db)
        make_produto(db)
        make_pedido(db, id="ped1")
        make_item_pedido(db, id_pedido="ped1", id_produto="prod01", preco=150.0, frete=15.0)
        body = client.get("/pedidos/ped1").json()
        assert body["total_itens"] == 1
        assert body["itens"][0]["id_produto"] == "prod01"
        assert body["itens"][0]["preco_BRL"] == 150.0

    def test_valor_total_calculado_corretamente(self, client, db):
        _infra(db)
        make_produto(db, id="p1")
        make_produto(db, id="p2", nome="Produto 2", categoria="livros")
        make_pedido(db, id="ped1")
        make_item_pedido(db, id_pedido="ped1", id_produto="p1", id_item=1, preco=100.0, frete=10.0)
        make_item_pedido(db, id_pedido="ped1", id_produto="p2", id_item=2, preco=200.0, frete=20.0)
        body = client.get("/pedidos/ped1").json()
        assert body["total_itens"] == 2
        assert body["valor_total"] == 330.0  # (100+10) + (200+20)

    def test_retorna_avaliacao_quando_existe(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        make_avaliacao(db, id="aval1", id_pedido="ped1", nota=4)
        body = client.get("/pedidos/ped1").json()
        assert body["avaliacao"] is not None
        assert body["avaliacao"]["avaliacao"] == 4
        assert body["avaliacao"]["id_pedido"] == "ped1"

    def test_avaliacao_none_quando_nao_existe(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        body = client.get("/pedidos/ped1").json()
        assert body["avaliacao"] is None


# ══════════════════════════════════════════════════════════════════════════════
# POST /pedidos
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarPedido:

    def test_cria_pedido_com_um_item(self, client, db):
        _infra(db)
        make_produto(db)
        resp = client.post("/pedidos", json=_payload_pedido())
        assert resp.status_code == 201
        body = resp.json()
        assert body["id_consumidor"] == "cons01"
        assert body["status"] == "pendente"
        assert body["total_itens"] == 1
        assert body["itens"][0]["preco_BRL"] == 100.0
        assert len(body["id_pedido"]) == 32

    def test_cria_pedido_com_multiplos_itens(self, client, db):
        _infra(db)
        make_produto(db, id="p1")
        make_produto(db, id="p2", nome="B", categoria="livros")
        payload = {
            "id_consumidor": "cons01",
            "status": "pendente",
            "itens": [
                {"id_produto": "p1", "id_vendedor": "vend01", "preco_BRL": 50.0, "preco_frete": 5.0},
                {"id_produto": "p2", "id_vendedor": "vend01", "preco_BRL": 80.0, "preco_frete": 8.0},
            ],
        }
        body = client.post("/pedidos", json=payload).json()
        assert body["total_itens"] == 2
        assert body["valor_total"] == 143.0  # (50+5) + (80+8)

    def test_valor_total_calculado_na_criacao(self, client, db):
        _infra(db)
        make_produto(db)
        body = client.post("/pedidos", json=_payload_pedido()).json()
        assert body["valor_total"] == 110.0  # 100 + 10

    def test_consumidor_inexistente_retorna_404(self, client):
        resp = client.post("/pedidos", json=_payload_pedido(id_consumidor="nao-existe"))
        assert resp.status_code == 404

    def test_itens_vazios_retorna_422(self, client, db):
        make_consumidor(db)
        payload = {"id_consumidor": "cons01", "status": "pendente", "itens": []}
        assert client.post("/pedidos", json=payload).status_code == 422

    def test_preco_negativo_retorna_422(self, client, db):
        make_consumidor(db)
        payload = {
            "id_consumidor": "cons01",
            "status": "pendente",
            "itens": [
                {"id_produto": "p1", "id_vendedor": "v1", "preco_BRL": -10.0, "preco_frete": 0.0}
            ],
        }
        assert client.post("/pedidos", json=payload).status_code == 422

    def test_pedido_aparece_na_listagem_apos_criacao(self, client, db):
        _infra(db)
        make_produto(db)
        client.post("/pedidos", json=_payload_pedido())
        assert client.get("/pedidos").json()["total"] == 1

    def test_ids_gerados_sao_unicos(self, client, db):
        _infra(db)
        make_produto(db)
        ids = {
            client.post("/pedidos", json=_payload_pedido()).json()["id_pedido"]
            for _ in range(5)
        }
        assert len(ids) == 5


# ══════════════════════════════════════════════════════════════════════════════
# PUT /pedidos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestAtualizarPedido:

    def test_atualiza_status(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="pendente")
        resp = client.put("/pedidos/ped1", json={"status": "entregue"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "entregue"

    def test_persistencia(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="pendente")
        client.put("/pedidos/ped1", json={"status": "cancelado"})
        assert client.get("/pedidos/ped1").json()["status"] == "cancelado"

    def test_404_para_id_inexistente(self, client):
        assert client.put("/pedidos/nao-existe", json={"status": "entregue"}).status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /pedidos/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDeletarPedido:

    def test_retorna_204(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        assert client.delete("/pedidos/ped1").status_code == 204

    def test_404_apos_delecao(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        client.delete("/pedidos/ped1")
        assert client.get("/pedidos/ped1").status_code == 404

    def test_some_da_listagem(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        client.delete("/pedidos/ped1")
        assert client.get("/pedidos").json()["total"] == 0

    def test_404_para_id_inexistente(self, client):
        assert client.delete("/pedidos/nao-existe").status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# POST /pedidos/{id}/avaliacao
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarAvaliacao:

    def test_404_pedido_inexistente(self, client):
        resp = client.post("/pedidos/nao-existe/avaliacao", json={"avaliacao": 5})
        assert resp.status_code == 404

    def test_cria_avaliacao(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        resp = client.post("/pedidos/ped1/avaliacao", json={
            "avaliacao": 5,
            "titulo_comentario": "Perfeito",
            "comentario": "Recomendo muito!",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["avaliacao"] == 5
        assert body["id_pedido"] == "ped1"
        assert body["titulo_comentario"] == "Perfeito"
        assert len(body["id_avaliacao"]) == 32

    def test_nota_zero_retorna_422(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        assert client.post("/pedidos/ped1/avaliacao", json={"avaliacao": 0}).status_code == 422

    def test_nota_acima_de_cinco_retorna_422(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01")
        assert client.post("/pedidos/ped1/avaliacao", json={"avaliacao": 6}).status_code == 422

    def test_avaliacao_duplicada_retorna_409(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        client.post("/pedidos/ped1/avaliacao", json={"avaliacao": 4})
        resp = client.post("/pedidos/ped1/avaliacao", json={"avaliacao": 5})
        assert resp.status_code == 409

    def test_avaliacao_aparece_no_detalhe_do_pedido(self, client, db):
        make_consumidor(db)
        make_pedido(db, id="ped1", id_consumidor="cons01", status="entregue")
        client.post("/pedidos/ped1/avaliacao", json={"avaliacao": 3})
        body = client.get("/pedidos/ped1").json()
        assert body["avaliacao"] is not None
        assert body["avaliacao"]["avaliacao"] == 3
