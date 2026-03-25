from unittest.mock import patch


PRODUTO_BASE = {
    "name": "Notebook Dell XPS 15",
    "url": "https://www.amazon.com.br/dp/B08N5M7S6K",
    "target_price": 3500.00,
    "email": "usuario@exemplo.com",
}


def test_criar_produto_retorna_201(client):
    response = client.post("/products/", json=PRODUTO_BASE)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == PRODUTO_BASE["name"]
    assert data["target_price"] == PRODUTO_BASE["target_price"]
    assert data["email"] == PRODUTO_BASE["email"]
    assert data["is_active"] is True
    assert data["current_price"] is None
    assert "id" in data


def test_criar_produto_valida_preco_negativo(client):
    payload = {**PRODUTO_BASE, "target_price": -100.00}
    response = client.post("/products/", json=payload)
    assert response.status_code == 422


def test_criar_produto_valida_email_invalido(client):
    payload = {**PRODUTO_BASE, "email": "nao-e-um-email"}
    response = client.post("/products/", json=payload)
    assert response.status_code == 422


def test_criar_produto_valida_url_invalida(client):
    payload = {**PRODUTO_BASE, "url": "nao-e-uma-url"}
    response = client.post("/products/", json=payload)
    assert response.status_code == 422


def test_listar_produtos_retorna_lista(client):
    client.post("/products/", json=PRODUTO_BASE)
    client.post(
        "/products/",
        json={
            **PRODUTO_BASE,
            "name": "Smartphone Samsung S24",
            "url": "https://www.mercadolivre.com.br/produto/123",
        },
    )
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_listar_produtos_retorna_lista_vazia(client):
    response = client.get("/products/")
    assert response.status_code == 200
    assert response.json() == []


def test_historico_produto_retorna_campos_corretos(client):
    resp = client.post("/products/", json=PRODUTO_BASE)
    product_id = resp.json()["id"]

    response = client.get(f"/products/{product_id}/history")
    assert response.status_code == 200

    data = response.json()
    assert data["product"] == PRODUTO_BASE["name"]
    assert data["target_price"] == PRODUTO_BASE["target_price"]
    assert data["current_price"] is None
    assert data["lowest_price"] is None
    assert data["highest_price"] is None
    assert data["history"] == []


def test_historico_produto_nao_encontrado(client):
    response = client.get("/products/9999/history")
    assert response.status_code == 404


def test_remover_produto_retorna_204(client):
    resp = client.post("/products/", json=PRODUTO_BASE)
    product_id = resp.json()["id"]

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204


def test_produto_removido_nao_aparece_na_listagem(client):
    resp = client.post("/products/", json=PRODUTO_BASE)
    product_id = resp.json()["id"]

    client.delete(f"/products/{product_id}")

    listagem = client.get("/products/").json()
    ids_ativos = [p["id"] for p in listagem]
    assert product_id not in ids_ativos


def test_remover_produto_nao_encontrado(client):
    response = client.delete("/products/9999")
    assert response.status_code == 404


def test_verificacao_manual_retorna_produto(client):
    resp = client.post("/products/", json=PRODUTO_BASE)
    product_id = resp.json()["id"]

    with patch("app.api.routes.products.check_product_price") as mock_check:
        mock_check.return_value = None
        response = client.post(f"/products/{product_id}/check")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    mock_check.assert_called_once_with(product_id)


def test_verificacao_manual_produto_nao_encontrado(client):
    with patch("app.api.routes.products.check_product_price"):
        response = client.post("/products/9999/check")
    assert response.status_code == 404


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
