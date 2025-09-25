"""
Módulo de roteamento da API v1.

Este módulo reúne todos os roteadores da API v1 e os expõe através de um único roteador.
"""

from fastapi import APIRouter

# Cria o roteador principal da API v1
api_router = APIRouter()

# Importa e inclui os roteadores específicos
# from .endpoints import criptomoedas, estatisticas, historico

# Inclui os roteadores
# api_router.include_router(criptomoedas.router, prefix="/criptomoedas", tags=["Criptomoedas"])
# api_router.include_router(estatisticas.router, prefix="/estatisticas", tags=["Estatísticas"])
# api_router.include_router(historico.router, prefix="/historico", tags=["Histórico"])
