"""
Ponto de entrada principal da aplicação FastAPI.

Este módulo configura e inicializa a aplicação FastAPI, incluindo middlewares,
roteadores e manipuladores de eventos.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.supabase import get_supabase
from app.models.base import ErrorResponse

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    
    Inicializa a conexão com o Supabase e outros recursos ao iniciar a aplicação.
    """
    # Código executado ao iniciar a aplicação
    logger.info("Iniciando a aplicação...")
    
    # Testa a conexão com o Supabase
    try:
        supabase = get_supabase()
        # Testa uma consulta simples para verificar a conexão
        result = supabase.table("cryptocurrencies").select("count", count="exact").limit(1).execute()
        logger.info("Conexão com o Supabase estabelecida com sucesso.")
        logger.debug(f"Resultado do teste de conexão: {result}")
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {str(e)}")
        raise
    
    yield  # A aplicação está rodando
    
    # Código executado ao encerrar a aplicação
    logger.info("Encerrando a aplicação...")


# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para fornecimento de dados de criptomoedas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configuração do CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclui o roteador principal da API
app.include_router(api_router, prefix=settings.API_V1_STR)


# Manipuladores de erros globais
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Manipulador global para erros de validação de requisição.
    """
    logger.error(f"Erro de validação: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Erro de validação",
            details={"errors": exc.errors()},
        ).dict(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Manipulador global para exceções não tratadas.
    """
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Erro interno do servidor",
            details={"message": str(exc)} if settings.DEBUG else {},
        ).dict(),
    )


# Endpoint de health check
@app.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Dicionário com o status da API.
    """
    return {"status": "ok"}


# Endpoint raiz
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """
    Endpoint raiz que redireciona para a documentação da API.
    
    Returns:
        Dicionário com links para a documentação da API.
    """
    return {
        "message": "Bem-vindo à API de Criptomoedas",
        "docs": "/docs",
        "redoc": "/redoc",
    }
