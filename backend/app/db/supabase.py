"""
Módulo de cliente Supabase.

Este módulo fornece uma instância configurada do cliente Supabase para interação
com o banco de dados PostgreSQL hospedado no Supabase.
"""

import logging
import os
from typing import Optional, Tuple

from supabase import Client, create_client
from fastapi import HTTPException

from app.core.config import settings

# Configuração de logging
logger = logging.getLogger(__name__)

# Inicialização dos clientes Supabase
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None


def get_supabase() -> Client:
    """
    Retorna a instância do cliente Supabase.
    
    Raises:
        HTTPException: Se o cliente Supabase não estiver configurado corretamente.
        
    Returns:
        Client: Instância do cliente Supabase.
    """
    global supabase
    
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            error_msg = "Configuração do Supabase ausente. Verifique as variáveis de ambiente."
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
        try:
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Cliente Supabase inicializado com sucesso.")
        except Exception as e:
            error_msg = f"Falha ao inicializar o cliente Supabase: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    return supabase


def get_supabase_admin() -> Client:
    """
    Retorna a instância do cliente Supabase com privilégios de administrador.
    
    Raises:
        HTTPException: Se o cliente Supabase admin não estiver configurado corretamente.
        
    Returns:
        Client: Instância do cliente Supabase com privilégios de administrador.
    """
    global supabase_admin
    
    if supabase_admin is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            error_msg = "Configuração do Supabase Admin ausente. Verifique as variáveis de ambiente."
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
        
        try:
            supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            logger.info("Cliente Supabase Admin inicializado com sucesso.")
        except Exception as e:
            error_msg = f"Falha ao inicializar o cliente Supabase Admin: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=error_msg
            )
    
    return supabase_admin


def test_connection() -> Tuple[bool, str]:
    """
    Testa a conexão com o Supabase.
    
    Returns:
        Tuple[bool, str]: Tupla contendo o status da conexão e uma mensagem descritiva.
    """
    try:
        client = get_supabase()
        # Tenta uma operação simples para verificar a conexão
        client.table('cryptocurrencies').select("count").limit(1).execute()
        return True, "Conexão com o Supabase estabelecida com sucesso."
    except Exception as e:
        error_msg = f"Erro ao conectar ao Supabase: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
