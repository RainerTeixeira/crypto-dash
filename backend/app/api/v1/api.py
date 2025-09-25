"""
Roteador principal da API v1.

Este módulo reúne todos os roteadores da API v1 e os expõe através de um único roteador.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import cryptocurrencies

# Cria o roteador principal da API v1
api_router = APIRouter()

# Inclui os roteadores de cada módulo
api_router.include_router(
    cryptocurrencies.router,
    prefix="/cryptocurrencies",
    tags=["Cryptocurrencies"]
)
