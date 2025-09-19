# API de Criptomoedas
# Este módulo implementa uma API RESTful para consulta de dados de criptomoedas
# Utiliza o framework FastAPI para criar os endpoints e o Supabase como banco de dados

# Importações necessárias
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
from supabase_client import supabase  # Cliente para acessar o banco de dados Supabase
from pydantic import BaseModel  # Para validação de dados

# Inicialização da aplicação FastAPI
# Configuração de metadados para documentação automática (Swagger/OpenAPI)
app = FastAPI(
    title="API de Criptomoedas",
    description="""
    API para consulta de preços e informações sobre criptomoedas.
    
    Esta API fornece dados em tempo real sobre as principais criptomoedas do mercado,
    incluindo preços, capitalização de mercado, volume de negociação e variação percentual.
    """,
    version="1.0.0"
)

# Configuração do CORS (Cross-Origin Resource Sharing)
# Permite que a API seja acessada a partir de diferentes origens (domínios)
app.add_middleware(
    CORS,
    allow_origins=["*"],  # Em produção, substituir por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Modelos Pydantic para validação e documentação dos dados
# Estes modelos definem a estrutura dos dados que a API retorna

class Criptomoeda(BaseModel):
    """Modelo que representa os dados de uma criptomoeda."""
    id: int
    name: str  # Nome da criptomoeda (ex: Bitcoin)
    symbol: str  # Símbolo (ex: BTC)
    price: float  # Preço atual em USD
    market_cap: Optional[float] = None  # Capitalização de mercado (opcional)
    volume_24h: Optional[float] = None  # Volume de negociação nas últimas 24h (opcional)
    change_24h: Optional[float] = None  # Variação percentual nas últimas 24h (opcional)
    last_updated: str  # Data/hora da última atualização

class MensagemErro(BaseModel):
    """Modelo para mensagens de erro padronizadas."""
    detalhe: str

# Endpoints da API

@app.get("/api/health", tags=["Monitoramento"])
async def verificar_saude():
    """
    Verifica o status da API.
    
    Este endpoint é útil para monitoramento e verificação de disponibilidade.
    
    Returns:
        dict: Dicionário contendo o status da API e timestamp atual
    """
    return {
        "status": "operacional", 
        "timestamp": datetime.utcnow().isoformat(),
        "versao": "1.0.0"
    }

@app.get(
    "/api/criptomoedas",
    response_model=List[Criptomoeda],
    responses={
        200: {"description": "Lista de criptomoedas retornada com sucesso"},
        500: {"model": MensagemErro, "description": "Erro interno do servidor"}
    },
    tags=["Criptomoedas"],
    summary="Lista todas as criptomoedas",
    description="""
    Retorna a lista de todas as criptomoedas cadastradas no sistema,
    ordenadas por capitalização de mercado em ordem decrescente.
    """
)
async def obter_criptomoedas():
    """
    Obtém a lista de todas as criptomoedas disponíveis.
    
    A lista é ordenada por capitalização de mercado (market cap) em ordem decrescente.
    
    Returns:
        List[Criptomoeda]: Lista de criptomoedas com seus respectivos dados
        
    Raises:
        HTTPException: Em caso de erro ao acessar o banco de dados
    """
    try:
        # Consulta o banco de dados para obter todas as criptomoedas
        # Ordena por market_cap em ordem decrescente
        resposta = supabase.table('crypto_prices')\
                         .select("*")\
                         .order("market_cap", desc=True)\
                         .execute()
        return resposta.data
    except Exception as erro:
        # Em caso de erro, retorna uma resposta de erro 500
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar criptomoedas: {str(erro)}"
        )

@app.get(
    "/api/criptomoedas/{nome_cripto}",
    response_model=Criptomoeda,
    responses={
        200: {"description": "Dados da criptomoeda retornados com sucesso"},
        404: {"model": MensagemErro, "description": "Criptomoeda não encontrada"},
        500: {"model": MensagemErro, "description": "Erro interno do servidor"}
    },
    tags=["Criptomoedas"],
    summary="Obtém dados de uma criptomoeda específica",
    description="""
    Retorna os dados detalhados de uma criptomoeda específica com base no nome.
    A busca é feita de forma não sensível a maiúsculas/minúsculas.
    """
)
async def obter_criptomoeda(nome_cripto: str):
    """
    Obtém os dados de uma criptomoeda específica.
    
    Args:
        nome_cripto (str): Nome ou parte do nome da criptomoeda desejada
        
    Returns:
        Criptomoeda: Dados da criptomoeda encontrada
        
    Raises:
        HTTPException 404: Se a criptomoeda não for encontrada
        HTTPException 500: Em caso de erro no servidor
    """
    try:
        # Busca a criptomoeda por nome (busca parcial, case-insensitive)
        resposta = supabase.table('crypto_prices')\
                         .select("*")\
                         .ilike('name', f'%{nome_cripto}%')\
                         .execute()
        
        # Se nenhuma criptomoeda for encontrada, retorna 404
        if not resposta.data:
            raise HTTPException(
                status_code=404,
                detail=f"Criptomoeda '{nome_cripto}' não encontrada"
            )
            
        # Retorna o primeiro resultado da busca
        return resposta.data[0]
    except HTTPException:
        # Propaga exceções HTTP (como 404) para cima
        raise
    except Exception as erro:
        # Trata outros erros como erros de servidor (500)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar criptomoeda: {str(erro)}"
        )

@app.get(
    "/api/criptomoedas/{nome_cripto}/historico",
    responses={
        200: {"description": "Histórico de preços retornado com sucesso"},
        500: {"model": MensagemErro, "description": "Erro interno do servidor"}
    },
    tags=["Histórico"],
    summary="Obtém o histórico de preços de uma criptomoeda",
    description="""
    Retorna o histórico de preços de uma criptomoeda para um determinado período.
    
    Nota: Atualmente, esta é uma implementação de exemplo que retorna dados mockados.
    """
)
async def obter_historico_precos(
    nome_cripto: str,
    dias: int = Query(7, description="Número de dias de histórico", ge=1, le=90)
):
    """
    Obtém o histórico de preços de uma criptomoeda.
    
    Args:
        nome_cripto (str): Nome da criptomoeda
        dias (int, optional): Número de dias de histórico desejado. Deve estar entre 1 e 90. Padrão: 7.
        
    Returns:
        dict: Dicionário contendo o histórico de preços
        
    Note:
        Esta é uma implementação de exemplo que retorna dados mockados.
        Em uma implementação real, você buscaria esses dados de um serviço
        de histórico de preços ou de um banco de dados de séries temporais.
    """
    try:
        # Em uma implementação real, você buscaria os dados históricos de um banco de dados
        # ou de uma API de histórico de preços, como a CoinGecko ou CoinMarketCap
        
        # Exemplo de resposta mockada
        return {
            "criptomoeda": nome_cripto,
            "periodo_dias": dias,
            "dados": [
                # Dados de exemplo (seriam preenchidos com dados reais)
                # {"data": "2023-01-01", "preco": 45000.00, "volume": 25000000000},
                # ...
            ],
            "observacao": "Esta é uma resposta de exemplo. Implemente a lógica real de busca de histórico."
        }
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico de preços: {str(erro)}"
        )

@app.get(
    "/api/estatisticas",
    tags=["Estatísticas"],
    summary="Obtém estatísticas do mercado de criptomoedas",
    description="""
    Retorna estatísticas gerais sobre o mercado de criptomoedas,
    incluindo capitalização total, volume de negociação e dominância de mercado.
    
    Nota: Atualmente, esta é uma implementação de exemplo que retorna dados mockados.
    """
)
async def obter_estatisticas():
    """
    Retorna estatísticas gerais sobre o mercado de criptomoedas.
    
    Returns:
        dict: Dicionário contendo as estatísticas do mercado
        
    Note:
        Esta é uma implementação de exemplo que retorna dados mockados.
        Em uma implementação real, você calcularia essas estatísticas com base
        nos dados mais recentes do seu banco de dados ou de uma API externa.
    """
    try:
        # Em uma implementação real, você calcularia essas estatísticas
        # com base nos dados do seu banco de dados ou de uma API externa
        
        # Exemplo de estatísticas mockadas
        return {
            "total_criptomoedas": 10000,  # Número total de criptomoedas listadas
            "volume_24h": 100000000000,  # Volume total de negociação nas últimas 24h (em USD)
            "capitalizacao_mercado": 2000000000000,  # Capitalização total de mercado (em USD)
            "dominancia_btc": 40.5,  # Porcentagem de dominância do Bitcoin
            "dominancia_eth": 18.2,  # Porcentagem de dominância do Ethereum
            "atualizado_em": datetime.utcnow().isoformat(),
            "observacao": "Estas são estatísticas de exemplo. Implemente a lógica real de cálculo."
        }
    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estatísticas: {str(erro)}"
        )
