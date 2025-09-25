"""
Modelos base e utilitários para validação de dados.

Este módulo contém as classes base para os modelos Pydantic usados na API,
além de funções auxiliares para validação de dados.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

# Tipo genérico para os dados de resposta
DataT = TypeVar('DataT')

class ResponseModel(GenericModel, Generic[DataT]):
    """Modelo genérico para respostas da API.
    
    Este modelo padroniza a estrutura das respostas da API, incluindo
    os dados, metadados e informações de paginação quando aplicável.
    """
    success: bool = True
    data: Optional[DataT] = None
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Modelo para respostas de erro da API.
    
    Padroniza a estrutura das mensagens de erro retornadas pela API.
    """
    success: bool = False
    error: str = Field(..., description="Mensagem de erro descritiva")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Detalhes adicionais sobre o erro"
    )
    error_code: Optional[str] = Field(
        None,
        description="Código de erro para referência"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp UTC do erro"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginationParams(BaseModel):
    """Parâmetros de paginação para consultas à API."""
    page: int = Field(1, ge=1, description="Número da página (começando em 1)")
    page_size: int = Field(
        10, 
        ge=1, 
        le=100, 
        description="Número de itens por página (máx. 100)"
    )


class PaginatedResponse(ResponseModel[DataT]):
    """Modelo para respostas paginadas."""
    total: int = Field(..., description="Número total de itens")
    page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Número total de páginas")
    
    @classmethod
    def from_paginated_query(
        cls, 
        data: List[DataT], 
        total: int, 
        page: int, 
        page_size: int
    ) -> 'PaginatedResponse[DataT]':
        """Cria uma resposta paginada a partir de uma consulta."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return cls(
            data=data,
            total=total,
            page=page,
            total_pages=total_pages,
            meta={
                "page_size": page_size,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        )
