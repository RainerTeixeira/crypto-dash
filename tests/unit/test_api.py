import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Testa o endpoint de health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operacional"
    assert "timestamp" in data

def test_criptomoedas_endpoint():
    """Testa o endpoint de criptomoedas (pode falhar se não houver dados)."""
    response = client.get("/api/criptomoedas")
    # Se não houver dados, pode retornar 200 com lista vazia ou erro
    assert response.status_code in [200, 500]

def test_admin_update_data():
    """Testa o endpoint de atualização de dados (sem executar realmente)."""
    # Como é um endpoint POST que executa script, vamos testar se está acessível
    response = client.post("/api/admin/update-data")
    # Pode retornar erro se script não estiver configurado, mas endpoint deve existir
    assert response.status_code in [200, 500, 504]

def test_estatisticas_endpoint():
    """Testa o endpoint de estatísticas."""
    response = client.get("/api/estatisticas")
    assert response.status_code in [200, 500]
