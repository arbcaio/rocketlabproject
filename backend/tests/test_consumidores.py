"""
Testes de integração — endpoints de Consumidores.

Cobertura:
  GET    /consumidores                 – listagem, busca, filtro, paginação
  GET    /consumidores/{id}            – detalhe
  POST   /consumidores                 – criação com validação
  PUT    /consumidores/{id}            – atualização parcial
  DELETE /consumidores/{id}            – remoção
  GET    /consumidores/{id}/pedidos    – pedidos do consumidor (com filtro de status)
"""

from tests.conftest import make_consumidor, make_pedido

_PAYLOAD = {
    "nome_consumidor": "João Silva",
    "prefixo_cep": "01310",
    "cidade": "São Paulo",
    "estado": "SP",
}


# ══════════════════════════════════════════════════════════════════════════════
# GET /consumidores
# ══════════════════════════════════════════════════════════════════════════════

class TestListarConsumidores:

    def test_lista_vazia(self, client):
        resp = client.get("/consumidores")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []
        assert body["pages"] == 1

    def test_retorna_consumidor_criado(self, client, db):
        make_consumidor(db, id="c1", nome="Ana Lima", cidade="Recife", estado="PE")
        body = client.get("/consumidores").json()
        assert body["total"] == 1
        item = body["items"][0]
        assert item["id_consumidor"] == "c1"
        assert item["nome_consumidor"] == "Ana Lima"
        assert item["estado"] == "PE"

    def test_busca_por_nome(self, client, db):
        make_consumidor(db, id="c1", nome="Carlos Souza", cidade="SP", estado="SP")
        make_consumidor(db, id="c2", nome="Maria Brito", cidade="RJ", estado="RJ")
        body = client.get("/consumidores?search=carlos").json()
        assert body["total"] == 1
        assert body["items"][0]["nome_consumidor"] == "Carlos Souza"

    def test_busca_por_cidade(self, client, db):
        make_consumidor(db, id="c1", nome="Ana", cidade="Fortaleza", estado="CE")
        make_consumidor(db, id="c2", nome="Bob", cidade="Salvador", estado="BA")
        body = client.get("/consumidores?search=fortaleza").json()
        assert body["total"] == 1
        assert body["items"][0]["cidade"] == "Fortaleza"

    def test_busca_case_insensitive(self, client, db):
        make_consumidor(db, id="c1", nome="Pedro Alves", cidade="Natal", estado="RN")
        assert client.get("/consumidores?search=PEDRO").json()["total"] == 1

    def test_busca_sem_resultado(self, client, db):
        make_consumidor(db, id="c1", nome="José Costa", cidade="BH", estado="MG")
        assert client.get("/consumidores?search=inexistente").json()["total"] == 0

    def test_filtro_por_estado(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="SP", estado="SP")
        make_consumidor(db, id="c2", nome="B", cidade="RJ", estado="RJ")
        make_consumidor(db, id="c3", nome="C", cidade="SP2", estado="SP")
        body = client.get("/consumidores?estado=SP").json()
        assert body["total"] == 2
        assert all(i["estado"] == "SP" for i in body["items"])

    def test_filtro_estado_case_insensitive(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="SP", estado="SP")
        assert client.get("/consumidores?estado=sp").json()["total"] == 1

    def test_paginacao(self, client, db):
        for i in range(5):
            make_consumidor(db, id=f"c{i}", nome=f"Consumidor {i}", cidade="X", estado="SP")
        body = client.get("/consumidores?page=1&page_size=2").json()
        assert body["total"] == 5
        assert body["pages"] == 3
        assert len(body["items"]) == 2

    def test_page_invalida_retorna_422(self, client):
        assert client.get("/consumidores?page=0").status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# GET /consumidores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDetalharConsumidor:

    def test_404_para_id_inexistente(self, client):
        assert client.get("/consumidores/nao-existe").status_code == 404

    def test_retorna_dados_corretos(self, client, db):
        make_consumidor(db, id="c1", nome="Luís Neto", cidade="Porto Alegre", estado="RS")
        body = client.get("/consumidores/c1").json()
        assert body["id_consumidor"] == "c1"
        assert body["nome_consumidor"] == "Luís Neto"
        assert body["cidade"] == "Porto Alegre"
        assert body["estado"] == "RS"


# ══════════════════════════════════════════════════════════════════════════════
# POST /consumidores
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarConsumidor:

    def test_cria_consumidor_completo(self, client):
        resp = client.post("/consumidores", json=_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["nome_consumidor"] == "João Silva"
        assert body["estado"] == "SP"
        assert len(body["id_consumidor"]) == 32  # uuid4().hex

    def test_nome_vazio_retorna_422(self, client):
        payload = {**_PAYLOAD, "nome_consumidor": ""}
        assert client.post("/consumidores", json=payload).status_code == 422

    def test_estado_invalido_retorna_422(self, client):
        """Estado com apenas 1 caractere deve falhar."""
        payload = {**_PAYLOAD, "estado": "S"}
        assert client.post("/consumidores", json=payload).status_code == 422

    def test_campos_obrigatorios_ausentes_retorna_422(self, client):
        assert client.post("/consumidores", json={"nome_consumidor": "X"}).status_code == 422
        assert client.post("/consumidores", json={}).status_code == 422

    def test_ids_gerados_sao_unicos(self, client):
        ids = {
            client.post("/consumidores", json={**_PAYLOAD, "nome_consumidor": f"C{i}"}).json()["id_consumidor"]
            for i in range(5)
        }
        assert len(ids) == 5

    def test_consumidor_aparece_na_listagem(self, client):
        client.post("/consumidores", json=_PAYLOAD)
        assert client.get("/consumidores").json()["total"] == 1


# ══════════════════════════════════════════════════════════════════════════════
# PUT /consumidores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestAtualizarConsumidor:

    def test_atualiza_nome(self, client, db):
        make_consumidor(db, id="c1", nome="Nome Antigo", cidade="SP", estado="SP")
        resp = client.put("/consumidores/c1", json={"nome_consumidor": "Nome Novo"})
        assert resp.status_code == 200
        assert resp.json()["nome_consumidor"] == "Nome Novo"

    def test_atualiza_cidade(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="Cidade Antiga", estado="SP")
        body = client.put("/consumidores/c1", json={"cidade": "Cidade Nova"}).json()
        assert body["cidade"] == "Cidade Nova"

    def test_partial_update_preserva_campos(self, client, db):
        make_consumidor(db, id="c1", nome="Original", cidade="Cidade X", estado="SP")
        body = client.put("/consumidores/c1", json={"nome_consumidor": "Atualizado"}).json()
        assert body["nome_consumidor"] == "Atualizado"
        assert body["cidade"] == "Cidade X"  # inalterado

    def test_persistencia(self, client, db):
        make_consumidor(db, id="c1", nome="Antigo", cidade="X", estado="SP")
        client.put("/consumidores/c1", json={"nome_consumidor": "Persistido"})
        assert client.get("/consumidores/c1").json()["nome_consumidor"] == "Persistido"

    def test_404_para_id_inexistente(self, client):
        assert client.put("/consumidores/nao-existe", json={"nome_consumidor": "X"}).status_code == 404

    def test_estado_invalido_retorna_422(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        assert client.put("/consumidores/c1", json={"estado": "S"}).status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# DELETE /consumidores/{id}
# ══════════════════════════════════════════════════════════════════════════════

class TestDeletarConsumidor:

    def test_retorna_204(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        assert client.delete("/consumidores/c1").status_code == 204

    def test_404_apos_delecao(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        client.delete("/consumidores/c1")
        assert client.get("/consumidores/c1").status_code == 404

    def test_some_da_listagem(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        client.delete("/consumidores/c1")
        assert client.get("/consumidores").json()["total"] == 0

    def test_404_para_id_inexistente(self, client):
        assert client.delete("/consumidores/nao-existe").status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# GET /consumidores/{id}/pedidos
# ══════════════════════════════════════════════════════════════════════════════

class TestPedidosConsumidor:

    def test_404_consumidor_inexistente(self, client):
        assert client.get("/consumidores/nao-existe/pedidos").status_code == 404

    def test_sem_pedidos(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        body = client.get("/consumidores/c1/pedidos").json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_retorna_pedidos_do_consumidor(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        make_pedido(db, id="ped1", id_consumidor="c1", status="entregue")
        make_pedido(db, id="ped2", id_consumidor="c1", status="pendente")
        body = client.get("/consumidores/c1/pedidos").json()
        assert body["total"] == 2

    def test_nao_retorna_pedidos_de_outro_consumidor(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        make_consumidor(db, id="c2", nome="B", cidade="Y", estado="RJ")
        make_pedido(db, id="ped1", id_consumidor="c2", status="entregue")
        body = client.get("/consumidores/c1/pedidos").json()
        assert body["total"] == 0

    def test_filtro_por_status(self, client, db):
        make_consumidor(db, id="c1", nome="A", cidade="X", estado="SP")
        make_pedido(db, id="ped1", id_consumidor="c1", status="entregue")
        make_pedido(db, id="ped2", id_consumidor="c1", status="pendente")
        body = client.get("/consumidores/c1/pedidos?status=entregue").json()
        assert body["total"] == 1
        assert body["items"][0]["status"] == "entregue"
