"""
Modelos relacionados a criptomoedas.

Este módulo contém os modelos Pydantic para validação e serialização
dos dados de criptomoedas retornados pela API.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic.types import confloat, conint

from app.models.base import ResponseModel


class CryptocurrencyBase(BaseModel):
    """Modelo base para dados de criptomoedas."""
    id: str = Field(..., description="ID único da criptomoeda")
    name: str = Field(..., description="Nome completo da criptomoeda")
    symbol: str = Field(..., description="Símbolo de ticker (ex: BTC, ETH)")
    
    class Config:
        orm_mode = True


class CryptocurrencyCreate(CryptocurrencyBase):
    """Modelo para criação de uma nova criptomoeda."""
    pass


class CryptocurrencyUpdate(BaseModel):
    """Modelo para atualização de dados de criptomoeda."""
    name: Optional[str] = Field(None, description="Novo nome da criptomoeda")
    symbol: Optional[str] = Field(None, description="Novo símbolo de ticker")
    price: Optional[float] = Field(None, description="Preço atual em USD")
    market_cap: Optional[float] = Field(None, description="Capitalização de mercado em USD")
    volume_24h: Optional[float] = Field(None, description="Volume de negociação nas últimas 24h em USD")
    change_24h: Optional[float] = Field(None, description="Variação percentual de preço nas últimas 24h")
    last_updated: Optional[datetime] = Field(None, description="Data e hora da última atualização")


class CryptocurrencyInDB(CryptocurrencyBase):
    """Modelo para dados de criptomoeda armazenados no banco de dados."""
    price: float = Field(..., description="Preço atual em USD")
    market_cap: Optional[float] = Field(None, description="Capitalização de mercado em USD")
    volume_24h: Optional[float] = Field(None, description="Volume de negociação nas últimas 24h em USD")
    change_24h: Optional[float] = Field(None, description="Variação percentual de preço nas últimas 24h")
    last_updated: datetime = Field(..., description="Data e hora da última atualização")
    
    @validator('last_updated', pre=True)
    def parse_last_updated(cls, v):
        """Garante que last_updated seja um objeto datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return v
        return v


class CryptocurrencyResponse(ResponseModel):
    """Resposta para uma única criptomoeda."""
    data: CryptocurrencyInDB


class CryptocurrencyListResponse(ResponseModel):
    """Resposta para uma lista de criptomoedas."""
    data: List[CryptocurrencyInDB]


class PriceHistoryPoint(BaseModel):
    """Ponto de dados para histórico de preços."""
    timestamp: datetime
    price: float
    volume: Optional[float] = None
    market_cap: Optional[float] = None


class PriceHistoryResponse(ResponseModel):
    """Resposta para histórico de preços de uma criptomoeda."""
    data: List[PriceHistoryPoint]


class MarketStats(BaseModel):
    """Estatísticas de mercado agregadas."""
    total_market_cap: float = Field(..., description="Capitalização de mercado total em USD")
    total_volume_24h: float = Field(..., description="Volume total de negociação nas últimas 24h em USD")
    active_cryptocurrencies: int = Field(..., description="Número total de criptomoedas ativas")
    btc_dominance: float = Field(..., description="Porcentagem de domínio do Bitcoin no mercado")
    eth_dominance: float = Field(..., description="Porcentagem de domínio do Ethereum no mercado")
    last_updated: datetime = Field(..., description="Data e hora da última atualização")


class MarketStatsResponse(ResponseModel):
    """Resposta para estatísticas de mercado."""
    data: MarketStats


class CryptocurrencyFilters(BaseModel):
    """Filtros para consulta de criptomoedas."""
    min_market_cap: Optional[float] = Field(None, description="Filtro por capitalização de mercado mínima")
    max_market_cap: Optional[float] = Field(None, description="Filtro por capitalização de mercado máxima")
    min_volume_24h: Optional[float] = Field(None, description="Filtro por volume mínimo nas últimas 24h")
    max_volume_24h: Optional[float] = Field(None, description="Filtro por volume máximo nas últimas 24h")
    min_price: Optional[float] = Field(None, description="Filtro por preço mínimo")
    max_price: Optional[float] = Field(None, description="Filtro por preço máximo")
    price_change_24h_min: Optional[float] = Field(None, description="Variação percentual de preço mínima nas últimas 24h")
    price_change_24h_max: Optional[float] = Field(None, description="Variação percentual de preço máxima nas últimas 24h")
    search: Optional[str] = Field(None, description="Termo de busca para nome ou símbolo")
    
    def to_supabase_filters(self) -> Dict[str, Any]:
        """Converte os filtros para o formato esperado pelo Supabase."""
        filters = {}
        
        if self.min_market_cap is not None:
            filters["market_cap"] = {"gte": self.min_market_cap}
        if self.max_market_cap is not None:
            filters["market_cap"] = {**filters.get("market_cap", {}), "lte": self.max_market_cap}
            
        if self.min_volume_24h is not None:
            filters["volume_24h"] = {"gte": self.min_volume_24h}
        if self.max_volume_24h is not None:
            filters["volume_24h"] = {**filters.get("volume_24h", {}), "lte": self.max_volume_24h}
            
        if self.min_price is not None:
            filters["price"] = {"gte": self.min_price}
        if self.max_price is not None:
            filters["price"] = {**filters.get("price", {}), "lte": self.max_price}
            
        if self.price_change_24h_min is not None:
            filters["change_24h"] = {"gte": self.price_change_24h_min}
        if self.price_change_24h_max is not None:
            filters["change_24h"] = {**filters.get("change_24h", {}), "lte": self.price_change_24h_max}
            
        if self.search:
            filters["or"] = [
                {"name": {"ilike": f"%{self.search}%"}},
                {"symbol": {"ilike": f"%{self.search}%"}}
            ]
            
        return filters
