"""
Endpoints para manipulação de dados de criptomoedas.

Este módulo contém os endpoints da API para listar, buscar, criar, atualizar
e excluir dados de criptomoedas.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.supabase import get_supabase
from app.models.base import PaginatedResponse, PaginationParams
from app.models.cryptocurrency import (
    CryptocurrencyCreate,
    CryptocurrencyFilters,
    CryptocurrencyInDB,
    CryptocurrencyListResponse,
    CryptocurrencyResponse,
    CryptocurrencyUpdate,
    MarketStats,
    MarketStatsResponse,
    PriceHistoryPoint,
    PriceHistoryResponse,
)

# Cria o roteador para os endpoints de criptomoedas
router = APIRouter(prefix="/cryptocurrencies", tags=["cryptocurrencies"])


@router.get(
    "/",
    response_model=PaginatedResponse[CryptocurrencyInDB],
    response_model_exclude_none=True,
    summary="Listar criptomoedas",
    description="Retorna uma lista paginada de criptomoedas com suporte a filtros e ordenação.",
)
async def list_cryptocurrencies(
    request: Request,
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=250, description="Itens por página"),
    sort_by: str = Query(
        "market_cap",
        description="Campo para ordenação",
        enum=["market_cap", "volume_24h", "price", "change_24h", "name", "symbol"],
    ),
    sort_order: str = Query(
        "desc",
        description="Direção da ordenação",
        regex="^(asc|desc)$",
    ),
    filters: CryptocurrencyFilters = Depends(),
) -> PaginatedResponse[CryptocurrencyInDB]:
    """
    Lista criptomoedas com suporte a paginação, ordenação e filtros.
    
    Args:
        request: Objeto de requisição FastAPI.
        page: Número da página (começando em 1).
        page_size: Número de itens por página (máx. 250).
        sort_by: Campo para ordenação.
        sort_order: Direção da ordenação (asc/desc).
        filters: Filtros de consulta.
        
    Returns:
        Resposta paginada com a lista de criptomoedas.
    """
    supabase = get_supabase()
    
    # Aplica os filtros
    query = supabase.table("cryptocurrencies").select("*", count="exact")
    
    # Aplica os filtros de pesquisa
    supabase_filters = filters.to_supabase_filters()
    for key, value in supabase_filters.items():
        if key == "or":
            for or_condition in value:
                query = query.or_(*[f"{k}.{list(v.keys())[0]}" for k, v in or_condition.items()])
        else:
            if isinstance(value, dict):
                for op, val in value.items():
                    query = query.filter(key, op, val)
            else:
                query = query.eq(key, value)
    
    # Aplica ordenação
    if sort_order.lower() == "asc":
        query = query.order(sort_by, desc=False)
    else:
        query = query.order(sort_by, desc=True)
    
    # Aplica paginação
    query = query.range((page - 1) * page_size, page * page_size - 1)
    
    # Executa a consulta
    result = query.execute()
    
    # Converte os resultados para o modelo Pydantic
    items = [CryptocurrencyInDB(**item) for item in result.data]
    total = result.count or 0
    
    # Retorna a resposta paginada
    return PaginatedResponse.from_paginated_query(
        data=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{crypto_id}",
    response_model=CryptocurrencyResponse,
    response_model_exclude_none=True,
    summary="Obter criptomoeda por ID",
    description="Retorna os detalhes de uma criptomoeda específica pelo seu ID.",
    responses={
        404: {"description": "Criptomoeda não encontrada"},
    },
)
async def get_cryptocurrency(
    crypto_id: str,
) -> CryptocurrencyResponse:
    """
    Obtém os detalhes de uma criptomoeda pelo seu ID.
    
    Args:
        crypto_id: ID da criptomoeda.
        
    Returns:
        Detalhes da criptomoeda.
        
    Raises:
        HTTPException: Se a criptomoeda não for encontrada.
    """
    supabase = get_supabase()
    
    # Tenta encontrar por ID primeiro
    result = supabase.table("cryptocurrencies").select("*").eq("id", crypto_id).execute()
    
    # Se não encontrar por ID, tenta pelo símbolo (case-insensitive)
    if not result.data:
        result = supabase.table("cryptocurrencies").select("*").ilike("symbol", crypto_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Criptomoeda com ID ou símbolo '{crypto_id}' não encontrada.",
        )
    
    return CryptocurrencyResponse(data=CryptocurrencyInDB(**result.data[0]))


@router.get(
    "/{crypto_id}/history",
    response_model=PriceHistoryResponse,
    summary="Obter histórico de preços",
    description="Retorna o histórico de preços de uma criptomoeda.",
    responses={
        404: {"description": "Criptomoeda não encontrada"},
    },
)
async def get_price_history(
    crypto_id: str,
    days: int = Query(7, ge=1, le=365, description="Número de dias de histórico"),
) -> PriceHistoryResponse:
    """
    Obtém o histórico de preços de uma criptomoeda.
    
    Args:
        crypto_id: ID ou símbolo da criptomoeda.
        days: Número de dias de histórico a serem retornados (máx. 365).
        
    Returns:
        Histórico de preços da criptomoeda.
        
    Raises:
        HTTPException: Se a criptomoeda não for encontrada.
    """
    # Primeiro, verifica se a criptomoeda existe
    await get_cryptocurrency(crypto_id)
    
    # Simula dados históricos (em um cenário real, isso viria do banco de dados)
    # Aqui você implementaria a lógica real para buscar os dados históricos
    # do banco de dados ou de uma API externa
    
    # Exemplo de dados simulados
    now = datetime.utcnow()
    history = []
    
    for i in range(days, 0, -1):
        timestamp = now - timedelta(days=i)
        # Gera um preço aleatório baseado no dia
        price = 50000 * (1 + (i % 7 - 3) * 0.05)  # Variação de ±15%
        volume = 1000000 * (1 + (i % 5 - 2) * 0.1)  # Volume variável
        
        history.append(
            PriceHistoryPoint(
                timestamp=timestamp,
                price=round(price, 2),
                volume=round(volume, 2),
                market_cap=price * 21000000,  # Aproximação para BTC
            )
        )
    
    return PriceHistoryResponse(data=history)


@router.get(
    "/market/stats",
    response_model=MarketStatsResponse,
    summary="Estatísticas do mercado",
    description="Retorna estatísticas agregadas do mercado de criptomoedas.",
)
async def get_market_stats() -> MarketStatsResponse:
    """
    Obtém estatísticas agregadas do mercado de criptomoedas.
    
    Returns:
        Estatísticas do mercado.
    """
    supabase = get_supabase()
    
    # Obtém o total de criptomoedas
    count_result = supabase.table("cryptocurrencies").select("id", count="exact").execute()
    total_cryptos = count_result.count or 0
    
    # Obtém as estatísticas agregadas
    stats_result = supabase.rpc(
        "get_market_stats",
        {},
        count=None,
    ).execute()
    
    # Se a função RPC não existir, calcula as estatísticas manualmente
    if not stats_result.data:
        # Consulta para obter a capitalização de mercado total
        market_cap_result = supabase.table("cryptocurrencies").select("market_cap").execute()
        total_market_cap = sum(item["market_cap"] for item in market_cap_result.data if item["market_cap"] is not None)
        
        # Consulta para obter o volume total das últimas 24h
        volume_result = supabase.table("cryptocurrencies").select("volume_24h").execute()
        total_volume_24h = sum(item["volume_24h"] for item in volume_result.data if item["volume_24h"] is not None)
        
        # Obtém a capitalização de mercado do BTC e ETH para calcular a dominância
        btc_result = supabase.table("cryptocurrencies").select("market_cap").eq("symbol", "BTC").execute()
        eth_result = supabase.table("cryptocurrencies").select("market_cap").eq("symbol", "ETH").execute()
        
        btc_market_cap = btc_result.data[0]["market_cap"] if btc_result.data else 0
        eth_market_cap = eth_result.data[0]["market_cap"] if eth_result.data else 0
        
        btc_dominance = (btc_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0
        eth_dominance = (eth_market_cap / total_market_cap * 100) if total_market_cap > 0 else 0
        
        stats = {
            "total_market_cap": total_market_cap,
            "total_volume_24h": total_volume_24h,
            "active_cryptocurrencies": total_cryptos,
            "btc_dominance": round(btc_dominance, 2),
            "eth_dominance": round(eth_dominance, 2),
            "last_updated": datetime.utcnow().isoformat(),
        }
    else:
        stats = stats_result.data[0]
    
    return MarketStatsResponse(data=MarketStats(**stats))
