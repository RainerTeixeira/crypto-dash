"""
Arquivo de configuração do pytest.
Este arquivo é carregado automaticamente pelo pytest antes de executar os testes.
"""
import os
import pytest
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env.test se existir
load_dotenv('.env.test')

# Configurações de fixtures podem ser adicionadas aqui
@pytest.fixture(scope="session")
def test_config():
    """Retorna a configuração de teste."""
    return {
        "TESTING": True,
        "DATABASE_URL": os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db"),
        "REDIS_URL": os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1"),
        "SUPABASE_URL": "https://mock-supabase-url.supabase.co",
        "SUPABASE_KEY": "mock-supabase-key"
    }
