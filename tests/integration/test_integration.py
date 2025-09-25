# -*- coding: utf-8 -*-
"""
Testes de integração para o painel de criptomoedas.

Estes testes verificam a integração entre diferentes componentes do sistema,
incluindo a comunicação com a API externa e o banco de dados.
"""

import pytest

from scripts.update_data import buscar_dados_criptomoedas, atualizar_banco_dados

# Marca este teste como de integração (requer serviços externos)
@pytest.mark.integration
class TestIntegracaoCompleta:
    """Testes de integração para o fluxo completo de atualização de dados."""
    
    def test_buscar_dados_criptomoedas_integracao(self):
        """
        Testa a busca de dados da API CoinGecko.
        
        Este teste faz uma chamada real para a API e verifica se os dados são retornados
        no formato esperado.
        """
        # Chama a função de busca de dados
        dados = buscar_dados_criptomoedas()
        
        # Verifica se a resposta não está vazia
        assert dados is not None
        assert isinstance(dados, list)
        
        # Verifica se os dados principais estão presentes
        if len(dados) > 0:
            primeiro_item = dados[0]
            assert 'id' in primeiro_item
            assert 'name' in primeiro_item
            assert 'current_price' in primeiro_item
    
    @pytest.mark.skip(reason="Requer configuração de banco de dados de teste")
    def test_atualizar_banco_dados_integracao(self, test_config):
        """
        Testa a atualização do banco de dados com dados de teste.
        
        Este teste requer um banco de dados de teste configurado corretamente.
        """
        # Dados de teste
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
        
        # Chama a função de atualização do banco de dados
        try:
            resultado = atualizar_banco_dados(dados_teste)
            assert resultado is not None
            # Aqui você pode adicionar mais verificações específicas
        except Exception as e:
            pytest.fail(f"Falha ao atualizar o banco de dados: {e}")
