"""
Package principal da aplicação FastAPI.

Este pacote contém a configuração e inicialização da aplicação FastAPI,
além de agrupar todos os submódulos da aplicação.
"""

from fastapi import FastAPI

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="API de Criptomoedas",
    description="API para fornecimento de dados de criptomoedas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Importa os roteadores após a criação do app para evitar importação circular
from .api.v1 import api_router

# Inclui o roteador principal
app.include_router(api_router, prefix="/api/v1")
