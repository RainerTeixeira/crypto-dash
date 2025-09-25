import pytest
from unittest.mock import patch, MagicMock
from scripts.update_data import buscar_dados_criptomoedas, atualizar_banco_dados

# Testes para a função buscar_dados_criptomoedas
@patch('scripts.update_data.requests.get')
def test_buscar_dados_criptomoedas_success(mock_get):
    # Configura o mock para retornar uma resposta de sucesso
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            'id': 'bitcoin',
            'symbol': 'btc',
            'name': 'Bitcoin',
            'current_price': 50000,
            'market_cap': 950000000000,
            'total_volume': 30000000000,
            'price_change_percentage_24h': 2.5,
            'last_updated': '2023-01-01T00:00:00Z'
        }
    ]
    mock_get.return_value = mock_response

    # Chama a função e verifica o resultado
    result = buscar_dados_criptomoedas()
    assert result is not None
    assert len(result) > 0
    assert 'Bitcoin' in [crypto['name'] for crypto in result]

@patch('scripts.update_data.requests.get')
def test_buscar_dados_criptomoedas_failure(mock_get):
    # Configura o mock para simular uma falha na requisição
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    # Verifica se a função retorna None em caso de erro
    assert buscar_dados_criptomoedas() is None

# Testes para a função atualizar_banco_dados
def test_atualizar_banco_dados():
    # Dados de exemplo para teste
    dados_teste = [
        {
            'id': 'bitcoin',
            'symbol': 'btc',
            'name': 'Bitcoin',
            'current_price': 50000,
            'market_cap': 950000000000,
            'total_volume': 30000000000,
            'price_change_percentage_24h': 2.5,
            'last_updated': '2023-01-01T00:00:00Z'
        }
    ]
    
    # Mock do cliente Supabase
    with patch('scripts.update_data.supabase') as mock_supabase:
        # Configura o mock para retornar uma resposta de sucesso
        mock_response = MagicMock()
        mock_response.data = dados_teste
        mock_supabase.table.return_value.upsert.return_value.execute.return_value = mock_response
        
        # Chama a função e verifica se não houve erros
        try:
            atualizar_banco_dados(dados_teste)
            assert True
        except Exception as e:
            pytest.fail(f"A função lançou uma exceção inesperada: {e}")

# Teste de integração (requer banco de dados de teste configurado)
@pytest.mark.integration
def test_integracao_completa():
    # Este teste requer um ambiente de teste configurado com um banco de dados real
    # Pode ser implementado posteriormente
    pass
