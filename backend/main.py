"""
@file main.py
@brief API RESTful principal para o painel de criptomoedas.

Este módulo implementa o backend da aplicação, utilizando o framework FastAPI para
expor dados de criptomoedas e estatísticas de mercado. Ele se conecta ao Supabase
(PostgreSQL) para buscar os dados que são periodicamente atualizados pelo script ETL,
e utiliza Redis para caching, otimizando as respostas da API.

Funcionalidades principais:
- Health check da API.
- Listagem paginada e ordenada de criptomoedas.
- Consulta de detalhes de criptomoedas por ID ou símbolo.
- Retorno de histórico de preços simulado para criptomoedas.
- Fornecimento de estatísticas globais do mercado.

Tecnologias Utilizadas:
- FastAPI: Framework web assíncrono de alta performance para construir APIs.
- Pydantic: Para validação de dados e serialização.
- Supabase: Backend-as-a-Service, provendo um banco de dados PostgreSQL.
- Redis: Utilizado como cache para otimizar as respostas da API.
- Uvicorn: Servidor ASGI para rodar a aplicação FastAPI.
"""

import os
import logging
import asyncio # Importado para uso com Redis asyncio
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Importações do FastAPI:
# FastAPI: A classe principal para criar a aplicação API.
# HTTPException: Para levantar erros HTTP padronizados.
# Query: Para definir parâmetros de query na URL.
# status: Para acessar códigos de status HTTP (ex: status.HTTP_200_OK).
# Request: Para acessar detalhes da requisição HTTP.
# CORSMiddleware: Para configurar as políticas de Cross-Origin Resource Sharing.
# JSONResponse: Para retornar respostas JSON personalizadas, especialmente com headers.
# Middleware: Para aplicar middlewares globais (como o de tratamento de erros).
from fastapi import FastAPI, HTTPException, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# Importações para Cache e Redis:
# FastAPICache: Biblioteca para integrar caching ao FastAPI.
# RedisBackend: Backend para FastAPICache que usa Redis.
# cache: Decorador para aplicar cache a endpoints da API.
# aioredis: Cliente Redis assíncrono para Python.
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

# Importações para o Banco de Dados:
# supabase: Instância do cliente Supabase para interagir com o banco de dados.
# supabase_admin: Instância do cliente Supabase com credenciais de admin (usada no ETL, não diretamente na API pública aqui).
from supabase_client import supabase, supabase_admin

# Importações para Modelos e Erros Personalizados:
# BaseModel, Field: Do Pydantic, para definir a estrutura dos dados (modelos).
# Removendo importações de erros personalizados pois o módulo 'middleware.error_handler' não existe.
# from middleware.error_handler import error_middleware, APIError, NotFoundError, ValidationError
from pydantic import BaseModel, Field

# Configuração de logging:
# Define o nível de log para INFO, mostrando mensagens informativas, warnings e erros.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gerenciador de ciclo de vida da aplicação FastAPI:
# Esta função é executada ao iniciar e ao encerrar a aplicação FastAPI.
# É um local ideal para inicializar recursos como conexões de banco de dados e cache.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    
    Inicializa a conexão com o Redis para cache e verifica a conexão com o Supabase
    ao iniciar a API. Garante que os recursos sejam fechados corretamente ao encerrar.
    """
    redis_connection = None # Variável para armazenar a conexão Redis
    try:
        # 1. Inicialização do Redis para o cache da API
        # Lê a URL do Redis das variáveis de ambiente. O padrão é 'redis://localhost:6379'.
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        logger.info(f"Conectando ao Redis em: {redis_url}")
        
        # Cria uma conexão assíncrona com o Redis.
        redis_connection = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        # Inicializa o FastAPICache com o backend Redis.
        # 'prefix' organiza as chaves de cache no Redis.
        FastAPICache.init(RedisBackend(redis_connection), prefix="crypto-cache")
        logger.info("Cache Redis inicializado com sucesso")
        
        # 2. Testa a conexão com o Supabase
        # Chama uma função RPC simples no Supabase para verificar a conexão.
        # 'version' é uma função fictícia ou uma função real para obter a versão do PostgreSQL.
        await supabase.rpc('version').execute() # Assume que 'version' é uma função existente ou mockada
        logger.info("Conexão com o Supabase verificada com sucesso")
        
        # 'yield' indica que a aplicação está pronta para receber requisições.
        yield
        
    except Exception as e:
        # Se ocorrer qualquer erro durante a inicialização, registra e levanta a exceção
        logger.error(f"Erro durante a inicialização da aplicação: {str(e)}", exc_info=True)
        raise # Levanta a exceção para impedir que a aplicação inicie com problemas
    finally:
        # Bloco finally garante que o Redis seja fechado, mesmo se houver erros.
        logger.info("Encerrando a aplicação e liberando recursos...")
        if redis_connection:
            await redis_connection.close()
            logger.info("Conexão com Redis encerrada")

# Inicialização da aplicação FastAPI:
# Cria uma instância da aplicação FastAPI com metadados para a documentação (Swagger UI).
app = FastAPI(
    title="API de Criptomoedas", # Título exibido na documentação da API
    description="""
    API para consulta de preços e informações sobre criptomoedas.
    
    Esta API fornece dados em tempo real sobre as principais criptomoedas do mercado,
    incluindo preços, capitalização de mercado, volume de negociação e variação percentual.
    """, # Descrição detalhada da API
    version="1.0.0", # Versão da API
    lifespan=lifespan, # Vincula a função de ciclo de vida à aplicação
    # Removendo o middleware de erro customizado, pois a pasta 'middleware' não existe.
    # middleware=[
    #     Middleware(error_middleware)
    # ]
)

# Configuração CORS (Cross-Origin Resource Sharing):
# Permite que o frontend (em um domínio/porta diferente) acesse esta API.
# É crucial para o desenvolvimento local (localhost:3000 -> localhost:8000).
origins = [
    "https://rainersoft.com.br", # Domínio de produção (exemplo)
    "https://www.rainersoft.com.br", # Outro domínio de produção (exemplo)
    "http://localhost:3000",      # Frontend Next.js em desenvolvimento
    "http://localhost:8000",      # A própria API (útil para testes diretos e Swagger UI)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Lista de origens permitidas
    allow_credentials=True,        # Permite o envio de cookies e cabeçalhos de autorização
    allow_methods=["*"],           # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],           # Permite todos os cabeçalhos nas requisições
    expose_headers=["Content-Length", "X-Request-ID"], # Cabeçalhos que o navegador pode acessar
    max_age=600,  # Tempo (em segundos) que o navegador pode armazenar a resposta de preflight CORS
)

# Modelos Pydantic para validação e documentação dos dados:
# Estes modelos definem a estrutura esperada dos dados que a API recebe e retorna.
# Eles são fundamentais para a validação automática e a geração da documentação interativa (Swagger UI).

class Criptomoeda(BaseModel):
    """
    Modelo Pydantic que representa os dados detalhados de uma criptomoeda.
    
    Esta interface é usada para:
    - Validar os dados antes de enviá-los ao cliente.
    - Gerar automaticamente a documentação (schema) na Swagger UI.
    """
    # ID único da criptomoeda no banco de dados. '...' indica que é um campo obrigatório.
    id: int = Field(..., description="ID único da criptomoeda no banco de dados")
    # Nome completo da criptomoeda, como 'Bitcoin'.
    name: str = Field(..., description="Nome completo da criptomoeda (ex: Bitcoin)")
    # Símbolo de ticker curto da criptomoeda, como 'btc'.
    symbol: str = Field(..., description="Símbolo de ticker da criptomoeda (ex: BTC)")
    # Preço atual da criptomoeda em USD.
    price: float = Field(..., description="Preço atual em USD")
    # Capitalização de mercado em USD. 'Optional' indica que o campo pode ser None.
    market_cap: Optional[float] = Field(None, description="Capitalização de mercado em USD")
    # Volume de negociação nas últimas 24 horas em USD. Também opcional.
    volume_24h: Optional[float] = Field(None, description="Volume de negociação nas últimas 24h em USD")
    # Variação percentual do preço nas últimas 24 horas. Opcional.
    change_24h: Optional[float] = Field(None, description="Variação percentual de preço nas últimas 24h")
    # Data e hora da última atualização dos dados, no formato ISO 8601.
    last_updated: str = Field(..., description="Data e hora da última atualização no formato ISO 8601")
    
    class Config:
        # Configurações internas do Pydantic para este modelo.
        schema_extra = {
            "example": { # Exemplo de dados para a documentação da API.
                "id": 1,
                "name": "Bitcoin",
                "symbol": "btc",
                "price": 50000.00,
                "market_cap": 950000000000,
                "volume_24h": 25000000000,
                "change_24h": 2.5,
                "last_updated": "2023-10-01T12:00:00Z"
            }
        }

class MensagemErro(BaseModel):
    """
    Modelo Pydantic para padronizar as mensagens de erro retornadas pela API.
    
    Isso garante que todas as respostas de erro tenham uma estrutura consistente,
    facilitando o tratamento de erros no frontend.
    """
    # Mensagem principal do erro, clara e descritiva.
    error: str = Field(..., description="Mensagem de erro descritiva")
    # Detalhes adicionais sobre o erro, útil para depuração.
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais sobre o erro")
    # ID de correlação, para rastrear uma requisição específica em logs.
    correlation_id: Optional[str] = Field(None, description="ID de correlação para rastreamento")
    # ID único do erro, para referência e busca em sistemas de monitoramento.
    error_id: Optional[str] = Field(None, description="ID único do erro para referência")
    
    class Config:
        schema_extra = {
            "example": { # Exemplo de estrutura de erro para a documentação.
                "error": "Recurso não encontrado",
                "details": {"resource": "criptomoeda", "id": 999},
                "correlation_id": "req_12345",
                "error_id": "err_67890"
            }
        }

# Endpoints da API:
# Cada endpoint define uma URL e um método HTTP (GET, POST, etc.) que o frontend ou outros serviços podem chamar.
# O FastAPI usa decoradores (@app.get, @app.post) para mapear funções Python a esses endpoints.

@app.get(
    "/api/health", 
    tags=["Monitoramento"], # Agrupa o endpoint na documentação (Swagger UI) sob a tag "Monitoramento"
    summary="Verifica o status da API", # Resumo curto do que o endpoint faz
    description="""
    Verifica a disponibilidade e o status da API.
    
    Este endpoint é útil para monitoramento de saúde (health check) e verificação 
    de disponibilidade da API. Retorna informações básicas sobre o status do serviço.
    """, # Descrição detalhada do endpoint
    responses={ # Define as possíveis respostas HTTP e seus exemplos, úteis para a documentação
        200: { # Código de status HTTP 200 (OK) significa sucesso
            "description": "API operacional",
            "content": {
                "application/json": {
                    "example": { # Exemplo de resposta JSON para este status
                        "status": "operacional",
                        "timestamp": "2023-10-01T12:00:00Z",
                        "versao": "1.0.0",
                        "ambiente": "production"
                    }
                }
            }
        }
    }
)
@cache(expire=30)  # Aplica cache: a resposta deste endpoint será armazenada no Redis por 30 segundos.
                   # Isso reduz a carga no servidor para requisições frequentes.
async def verificar_saude(request: Request): # A função assíncrona que lida com a requisição para este endpoint.
    """
    Endpoint de health check da API.
    
    Retorna o status 'operacional' junto com metadados como timestamp, versão,
    ambiente e um ID de requisição para rastreamento (correlation_id).
    
    Args:
        request (Request): Objeto da requisição HTTP, fornecido automaticamente pelo FastAPI.
        
    Returns:
        dict: Um dicionário contendo o status e metadados da API.
    """
    # Retorna um dicionário que será automaticamente convertido para JSON pelo FastAPI.
    return {
        "status": "operacional", 
        "timestamp": datetime.utcnow().isoformat() + "Z", # Data e hora atual em formato ISO 8601 (UTC)
        "versao": "1.0.0",
        "ambiente": os.getenv("ENVIRONMENT", "development"), # Lê o ambiente das variáveis de ambiente, padrão é 'development'
        "request_id": request.state.correlation_id # ID único para rastrear a requisição nos logs
    }

@app.get(
    "/api/criptomoedas",
    response_model=List[Criptomoeda], # Define que a resposta será uma lista do modelo Criptomoeda
    responses={
        200: {
            "description": "Lista de criptomoedas retornada com sucesso",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Bitcoin",
                            "symbol": "btc",
                            "price": 50000.00,
                            "market_cap": 950000000000,
                            "volume_24h": 25000000000,
                            "change_24h": 2.5,
                            "last_updated": "2023-10-01T12:00:00Z"
                        }
                    ]
                }
            }
        },
        500: {"model": MensagemErro, "description": "Erro interno do servidor"} # Exemplo de erro 500
    },
    tags=["Criptomoedas"],
    summary="Lista todas as criptomoedas",
    description="""
    Retorna a lista de todas as criptomoedas cadastradas no sistema,
    ordenadas por capitalização de mercado em ordem decrescente.
    
    A lista pode ser filtrada e ordenada usando parâmetros de consulta.
    """
)
@cache(expire=60)  # Cache de 60 segundos para reduzir carga no banco de dados.
async def obter_criptomoedas(
    request: Request,
    pagina: int = Query(1, description="Número da página", ge=1), # Parâmetro de query para paginação, padrão 1, mínimo 1
    itens_por_pagina: int = Query(50, description="Itens por página", ge=1, le=250), # Parâmetro de query, padrão 50, entre 1 e 250
    ordem: str = Query("market_cap", description="Campo para ordenação", 
                      enum=["market_cap", "volume_24h", "price", "change_24h"]), # Campo para ordenar, com opções pré-definidas
    direcao: str = Query("desc", description="Direção da ordenação", 
                         regex="^(asc|desc)$") # Direção (ascendente/descendente), validado por regex
):
    """
    Endpoint para obter uma lista paginada de criptomoedas.
    
    Permite paginar, ordenar por diferentes campos (capitalização de mercado, volume, preço, variação de 24h)
    e definir a direção da ordenação (ascendente ou descendente).
    
    Args:
        request (Request): Objeto da requisição HTTP.
        pagina (int): O número da página desejada (começa em 1).
        itens_por_pagina (int): O número de criptomoedas por página (máximo de 250).
        ordem (str): O campo pelo qual as criptomoedas devem ser ordenadas.
        direcao (str): A direção da ordenação ('asc' para ascendente, 'desc' para descendente).
        
    Returns:
        JSONResponse: Uma resposta JSON contendo a lista de criptomoedas e cabeçalhos de paginação.
        
    Raises:
        APIError: Em caso de erro ao buscar os dados do banco de dados.
    """
    try:
        logger.info(
            "Consulta de criptomoedas - Página: %d, Itens: %d, Ordem: %s %s (request_id=%s)",
            pagina, itens_por_pagina, ordem, direcao.upper(), request.state.correlation_id
        )
        
        # Calcula o offset (deslocamento) para a paginação no banco de dados.
        offset = (pagina - 1) * itens_por_pagina
        
        # Constrói e executa a consulta ao Supabase.
        # .table('crypto_prices'): Seleciona a tabela 'crypto_prices'.
        # .select("*"): Seleciona todas as colunas.
        # .order(ordem, desc=(direcao.lower() == 'desc')): Ordena pelos campos e direção especificados.
        # .range(offset, offset + itens_por_pagina - 1): Limita os resultados para a paginação.
        query = (
            supabase.table('crypto_prices')
            .select("*")
            .order(ordem, desc=(direcao.lower() == 'desc'))
            .range(offset, offset + itens_por_pagina - 1)
        )
        
        resposta = query.execute()
        
        # Obtém o total de itens e calcula o total de páginas para os cabeçalhos de paginação.
        # Isso é importante para o frontend saber quantos dados totais existem.
        total_itens = len(supabase.table('crypto_prices').select("id", count='exact').execute().data or [])
        total_paginas = (total_itens + itens_por_pagina - 1) // itens_por_pagina
        
        # Define os cabeçalhos personalizados para a paginação.
        headers = {
            "X-Total-Count": str(total_itens),
            "X-Total-Pages": str(total_paginas),
            "X-Current-Page": str(pagina),
            "X-Items-Per-Page": str(itens_por_pagina),
            "X-Request-ID": request.state.correlation_id
        }
        
        # Retorna a resposta JSON com os dados e os cabeçalhos de paginação.
        return JSONResponse(
            content=resposta.data,
            headers=headers
        )
        
    except Exception as erro:
        # Em caso de erro, registra no log e levanta uma exceção APIError padronizada.
        logger.error(
            "Erro ao buscar criptomoedas: %s (request_id=%s)", 
            str(erro), getattr(request.state, 'correlation_id', 'none'),
            exc_info=True # Inclui informações de rastreamento da exceção no log
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar lista de criptomoedas"
        )

@app.get(
    "/api/criptomoedas/{id_ou_simbolo}", # Define um parâmetro de caminho dinâmico: id_ou_simbolo
    response_model=Criptomoeda, # Espera-se que a resposta seja um objeto Criptomoeda
    responses={
        200: {
            "description": "Dados da criptomoeda retornados com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Bitcoin",
                        "symbol": "btc",
                        "price": 50000.00,
                        "market_cap": 950000000000,
                        "volume_24h": 25000000000,
                        "change_24h": 2.5,
                        "last_updated": "2023-10-01T12:00:00Z"
                    }
                }
            }
        },
        400: {"model": MensagemErro, "description": "Requisição inválida"},
        404: {"model": MensagemErro, "description": "Criptomoeda não encontrada"},
        500: {"model": MensagemErro, "description": "Erro interno do servidor"}
    },
    tags=["Criptomoedas"],
    summary="Obtém dados de uma criptomoeda específica",
    description="""
    Retorna os dados detalhados de uma criptomoeda específica com base no ID ou símbolo.
    
    A busca pode ser feita pelo ID numérico ou pelo símbolo da criptomoeda (case-insensitive).
    """
)
@cache(expire=30)  # Cache de 30 segundos para reduzir carga
async def obter_criptomoeda(
    request: Request,
    id_ou_simbolo: str, # O valor do parâmetro de caminho, pode ser um ID ou símbolo
    incluir_historico: bool = Query(False, description="Incluir histórico de preços") # Parâmetro de query opcional
):
    """
    Endpoint para obter os dados detalhados de uma única criptomoeda.
    
    A busca pode ser realizada tanto pelo ID numérico quanto pelo símbolo da criptomoeda.
    Existe um parâmetro opcional para incluir um link para o histórico de preços (simulado).
    
    Args:
        request (Request): Objeto da requisição HTTP.
        id_ou_simbolo (str): O ID numérico (ex: '1') ou o símbolo (ex: 'btc') da criptomoeda.
        incluir_historico (bool): Se True, adiciona um campo 'historico' na resposta com URLs para o histórico (atualmente simulado).
        
    Returns:
        Criptomoeda: O objeto Criptomoeda correspondente.
        
    Raises:
        NotFoundError: Se a criptomoeda com o ID ou símbolo fornecido não for encontrada.
        APIError: Em caso de outros erros internos do servidor.
    """
    try:
        logger.info(
            "Consulta de criptomoeda: %s (request_id=%s, incluir_historico=%s)",
            id_ou_simbolo, request.state.correlation_id, incluir_historico
        )
        
        # Tenta converter o parâmetro para um número inteiro. Se conseguir, busca por ID.
        # Se falhar (ValueError), significa que é um símbolo, então busca por símbolo.
        try:
            crypto_id = int(id_ou_simbolo)
            query = supabase.table('crypto_prices').select("*").eq('id', crypto_id)
        except ValueError:
            # Busca por símbolo, usando 'ilike' para ser case-insensitive.
            query = supabase.table('crypto_prices').select("*").ilike('symbol', id_ou_simbolo.lower())
        
        # Executa a consulta no Supabase.
        resposta = query.execute()
        
        # Se nenhuma criptomoeda for encontrada, levanta um erro 404.
        if not resposta.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Criptomoeda '{id_ou_simbolo}' não encontrada"
            )
        
        # Pega a primeira criptomoeda encontrada (deve ser única).
        crypto_data = resposta.data[0]
        
        # Se o parâmetro 'incluir_historico' for True, adiciona links simulados para o histórico.
        if incluir_historico:
            # NOTA DIDÁTICA: Esta é uma implementação simplificada para demonstração.
            # Em um cenário real, você buscaria de uma tabela de histórico dedicada ou de uma API externa.
            crypto_data["historico"] = {
                "dias_30": f"/api/criptomoedas/{id_ou_simbolo}/historico?dias=30",
                "dias_90": f"/api/criptomoedas/{id_ou_simbolo}/historico?dias=90",
                "dias_365": f"/api/criptomoedas/{id_ou_simbolo}/historico?dias=365"
            }
        
        return crypto_data # Retorna os dados da criptomoeda.
        
    except HTTPException:
        # Erros HTTPException são propagados diretamente.
        raise
        
    except Exception as erro:
        # Qualquer outro erro é capturado, logado e transformado em um APIError padronizado (erro 500).
        logger.error(
            "Erro ao buscar criptomoeda %s: %s (request_id=%s)", 
            id_ou_simbolo, str(erro), request.state.correlation_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar criptomoeda: {str(erro)}"
        )

@app.get(
    "/api/criptomoedas/{id_ou_simbolo}/historico", # Endpoint para histórico, com parâmetro de caminho
    # Note que não usamos response_model aqui, pois o formato pode ser mais complexo e variável para históricos.
    responses={
        200: {
            "description": "Histórico de preços retornado com sucesso",
            "content": {
                "application/json": {
                    "example": { # Exemplo de resposta para o histórico
                        "criptomoeda": {"id": 1, "name": "Bitcoin", "symbol": "btc"},
                        "periodo_dias": 30,
                        "moeda": "usd",
                        "dados": [
                            {"data": "2023-09-01T00:00:00Z", "preco": 45000.00, "volume": 22000000000},
                            {"data": "2023-09-02T00:00:00Z", "preco": 45500.00, "volume": 23000000000}
                        ]
                    }
                }
            }
        },
        400: {"model": MensagemErro, "description": "Parâmetros inválidos"},
        404: {"model": MensagemErro, "description": "Criptomoeda não encontrada"},
        500: {"model": MensagemErro, "description": "Erro ao processar a requisição"}
    },
    tags=["Histórico"], # Agrupa sob a tag "Histórico"
    summary="Obtém o histórico de preços de uma criptomoeda",
    description="""
    Retorna o histórico de preços de uma criptomoeda para um determinado período.
    
    O histórico inclui preços de fechamento diários e volumes de negociação.
    """
)
@cache(expire=3600)  # Cache de 1 hora (3600 segundos) para dados históricos, que mudam menos frequentemente.
async def obter_historico_precos(
    request: Request,
    id_ou_simbolo: str, # ID ou símbolo da criptomoeda
    dias: int = Query(7, description="Número de dias de histórico (máx. 365)", ge=1, le=365), # Quantidade de dias de histórico, padrão 7, entre 1 e 365
    moeda: str = Query("usd", description="Moeda de conversão", regex="^[a-z]{3}$") # Moeda para os preços, padrão usd, validado por regex
):
    """
    Endpoint para fornecer dados históricos de preços de criptomoedas (atualmente simulados).
    
    Permite especificar a criptomoeda por ID ou símbolo, o número de dias de histórico
    e a moeda de referência.
    
    Args:
        request (Request): Objeto da requisição HTTP.
        id_ou_simbolo (str): O ID numérico ou o símbolo da criptomoeda para a qual o histórico é solicitado.
        dias (int): O número de dias de histórico desejado (entre 1 e 365).
        moeda (str): A moeda na qual os preços históricos devem ser apresentados (ex: 'usd').
        
    Returns:
        dict: Um dicionário contendo os dados da criptomoeda, período e uma lista de dados históricos simulados.
        
    Raises:
        NotFoundError: Se a criptomoeda não for encontrada.
        APIError: Em caso de outros erros internos do servidor.
    """
    try:
        logger.info(
            "Consulta de histórico - Cripto: %s, Dias: %d, Moeda: %s (request_id=%s)",
            id_ou_simbolo, dias, moeda.upper(), request.state.correlation_id
        )
        
        # 1. Primeiro, verifica se a criptomoeda existe no banco de dados.
        try:
            # Tenta buscar por ID numérico.
            try:
                crypto_id = int(id_ou_simbolo)
                query = supabase.table('crypto_prices').select('id,name,symbol').eq('id', crypto_id)
            except ValueError:
                # Se não for um ID, tenta buscar por símbolo.
                query = supabase.table('crypto_prices').select('id,name,symbol').ilike('symbol', id_ou_simbolo.lower())
            
            resultado = query.execute()
            
            if not resultado.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Criptomoeda '{id_ou_simbolo}' não encontrada"
                )
            
            crypto_info = resultado.data[0] # Informações básicas da criptomoeda.
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Erro ao verificar criptomoeda para histórico: %s", str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao verificar criptomoeda"
            )
        
        # 2. Busca dados históricos reais do banco de dados:
        try:
            # Usa a função RPC para buscar dados históricos reais
            crypto_id_for_history = crypto_info['id'] if 'id' in crypto_info else id_ou_simbolo
            
            # Chama a função RPC get_crypto_history
            historical_result = supabase.rpc('get_crypto_history', {
                'crypto_id_param': crypto_id_for_history,
                'days_param': dias
            }).execute()
            
            if historical_result.data:
                dados_historicos = [
                    {
                        "data": item['data'].isoformat() + "Z",
                        "preco": float(item['preco']),
                        "volume": float(item['volume']) if item['volume'] else 0
                    }
                    for item in historical_result.data
                ]
                logger.info(f"✅ Dados históricos reais obtidos: {len(dados_historicos)} registros")
            else:
                # Fallback: gera dados simulados se não houver dados históricos
                logger.warning("⚠️ Nenhum dado histórico encontrado. Usando dados simulados como fallback.")
                dados_historicos = []
                data_atual = datetime.utcnow()
                
                for i in range(dias, 0, -1):
                    data = data_atual - timedelta(days=i)
                    preco_base = 45000 + (hash(f"{id_ou_simbolo}{i}") % 10000) / 100
                    volume_base = 20000000000 + (hash(f"vol{id_ou_simbolo}{i}") % 10000000000)
                    
                    dados_historicos.append({
                        "data": data.isoformat() + "Z",
                        "preco": round(preco_base, 2),
                        "volume": int(volume_base)
                    })
                    
        except Exception as e:
            logger.warning(f"⚠️ Erro ao buscar dados históricos reais: {e}. Usando dados simulados.")
            # Fallback para dados simulados em caso de erro
            dados_historicos = []
            data_atual = datetime.utcnow()
            
            for i in range(dias, 0, -1):
                data = data_atual - timedelta(days=i)
                preco_base = 45000 + (hash(f"{id_ou_simbolo}{i}") % 10000) / 100
                volume_base = 20000000000 + (hash(f"vol{id_ou_simbolo}{i}") % 10000000000)
                
                dados_historicos.append({
                    "data": data.isoformat() + "Z",
                    "preco": round(preco_base, 2),
                    "volume": int(volume_base)
                })
        
        # 3. Retorna os dados históricos (reais ou simulados).
        return {
            "criptomoeda": { # Informações básicas da criptomoeda
                "id": crypto_info["id"],
                "name": crypto_info["name"],
                "symbol": crypto_info["symbol"].upper()
            },
            "periodo_dias": dias, # Período do histórico em dias
            "moeda": moeda.lower(), # Moeda de referência
            "dados": dados_historicos, # A lista de dados diários
            "atualizado_em": datetime.utcnow().isoformat() + "Z", # Timestamp da geração da resposta
            "observacao": "Dados históricos obtidos do banco de dados. Em caso de indisponibilidade, dados simulados são usados como fallback."
        }
        
    except HTTPException:
        # Propaga erros do tipo HTTPException (já tratados)
        raise
        
    except Exception as erro:
        # Captura e trata qualquer outra exceção inesperada.
        logger.error(
            "Erro ao buscar histórico para %s: %s (request_id=%s)", 
            id_ou_simbolo, str(erro), request.state.correlation_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico de preços: {str(erro)}"
        )

@app.get(
    "/api/estatisticas",
    # Note que não usamos response_model aqui, pois a estrutura das estatísticas pode ser flexível.
    responses={
        200: {
            "description": "Estatísticas do mercado retornadas com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "total_criptomoedas": 12345,
                        "volume_24h": 123456789012,
                        "capitalizacao_mercado": 1234567890123,
                        "dominancia_btc": 40.5,
                        "dominancia_eth": 18.2,
                        "maiores_ganhadores": [
                            {"id": 1, "symbol": "BTC", "change_24h": 5.2},
                            {"id": 1027, "symbol": "ETH", "change_24h": 3.8}
                        ],
                        "maiores_perdedores": [
                            {"id": 52, "symbol": "XRP", "change_24h": -2.1},
                            {"id": 2010, "symbol": "ADA", "change_24h": -1.7}
                        ],
                        "atualizado_em": "2023-10-01T12:00:00Z"
                    }
                }
            }
        },
        500: {"model": MensagemErro, "description": "Erro ao processar a requisição"}
    },
    tags=["Estatísticas"],
    summary="Obtém estatísticas do mercado de criptomoedas",
    description="""
    Retorna estatísticas gerais sobre o mercado de criptomoedas,
    incluindo capitalização total, volume de negociação e dominância de mercado.
    """
)
@cache(expire=300)  # Cache de 5 minutos (300 segundos) para estatísticas, pois elas mudam mais devagar que preços individuais.
async def obter_estatisticas(request: Request):
    """
    Endpoint para obter estatísticas gerais do mercado de criptomoedas.
    
    As estatísticas incluem o número total de criptomoedas, volume de negociação,
    capitalização de mercado, dominância do BTC/ETH e listas dos maiores ganhadores e perdedores.
    
    Returns:
        dict: Um dicionário contendo as estatísticas agregadas do mercado.
        
    Raises:
        APIError: Em caso de erro ao buscar os dados do banco de dados ou processar a requisição.
    """
    try:
        logger.info("Consulta de estatísticas do mercado (request_id=%s)", request.state.correlation_id)
        
        # 1. Obtenção do total de criptomoedas:
        # Consulta a tabela 'crypto_prices' para contar o número total de IDs.
        total_criptos = len(supabase.table('crypto_prices').select('id', count='exact').execute().data or [])
        
        # 2. Obtenção de outras estatísticas de mercado usando função RPC:
        try:
            resultado = supabase.rpc('get_market_stats').execute()
            
            if resultado.data and len(resultado.data) > 0:
                stats = resultado.data[0]
                logger.info("✅ Estatísticas de mercado obtidas via RPC")
            else:
                # Fallback para valores padrão se a RPC não retornar dados
                logger.warning("⚠️ RPC 'get_market_stats' não retornou dados. Usando valores padrão.")
                stats = {
                    "volume_24h": 100000000000,
                    "market_cap": 2000000000000,
                    "btc_dominance": 40.5,
                    "eth_dominance": 18.2
                }
        except Exception as e:
            logger.warning(f"⚠️ Erro ao chamar RPC 'get_market_stats': {e}. Usando valores padrão.")
            stats = {
                "volume_24h": 100000000000,
                "market_cap": 2000000000000,
                "btc_dominance": 40.5,
                "eth_dominance": 18.2
            }
        
        # 3. Obtenção dos maiores ganhadores usando função RPC:
        try:
            top_gainers_result = supabase.rpc('get_top_gainers', {'limit_param': 5}).execute()
            top_gainers = top_gainers_result.data if top_gainers_result.data else []
            logger.info(f"✅ Top gainers obtidos via RPC: {len(top_gainers)} registros")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter top gainers via RPC: {e}. Usando consulta direta.")
            top_gainers = (supabase.table('latest_prices')
                          .select('cryptocurrency_id,symbol,change_24h')
                          .order('change_24h', desc=True)
                          .limit(5)
                          .execute().data or [])
        
        # 4. Obtenção dos maiores perdedores usando função RPC:
        try:
            top_losers_result = supabase.rpc('get_top_losers', {'limit_param': 5}).execute()
            top_losers = top_losers_result.data if top_losers_result.data else []
            logger.info(f"✅ Top losers obtidos via RPC: {len(top_losers)} registros")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter top losers via RPC: {e}. Usando consulta direta.")
            top_losers = (supabase.table('latest_prices')
                         .select('cryptocurrency_id,symbol,change_24h')
                         .order('change_24h')
                         .limit(5)
                         .execute().data or [])
        
        # 5. Retorna as estatísticas agregadas.
        return {
            "total_criptomoedas": total_criptos,
            "volume_24h": stats.get("volume_24h", 0), # Usa .get() com valor padrão para evitar KeyError
            "capitalizacao_mercado": stats.get("market_cap", 0),
            "dominancia_btc": stats.get("btc_dominance", 0),
            "dominancia_eth": stats.get("eth_dominance", 0),
            "maiores_ganhadores": top_gainers,
            "maiores_perdedores": top_losers,
            "atualizado_em": datetime.utcnow().isoformat() + "Z" # Timestamp da geração da resposta
        }
        
    except Exception as erro:
        # Captura e trata qualquer exceção inesperada, formatando-a como APIError.
        logger.error(
            "Erro ao buscar estatísticas do mercado: %s (request_id=%s)", 
            str(erro), request.state.correlation_id,
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar estatísticas do mercado"
        )
