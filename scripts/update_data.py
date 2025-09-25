"""
@file update_data.py
@brief Script principal do processo ETL (Extração, Transformação, Carga) de criptomoedas.

Este script é responsável por automatizar a coleta, processamento e armazenamento de dados
de criptomoedas da API CoinGecko, utilizando Redis para cache e armazenamento. Ele foi projetado para ser
robusto, com tratamento de erros, retries, caching e processamento em lotes, garantindo
uma atualização eficiente e contínua dos dados de mercado.

Funcionalidades principais:
- Extração (Extract): Coleta dados de mercado de criptomoedas da CoinGecko, utilizando cache Redis.
- Transformação (Transform): Valida, limpa e padroniza os dados brutos.
- Armazenamento (Store): Armazena os dados processados no Redis para acesso rápido.
- Cache Inteligente: Gerencia automaticamente o cache para otimizar o uso da API.
- Ciclo Contínuo: Pode ser executado em um loop contínuo para manter os dados atualizados em intervalos regulares.

Tecnologias Utilizadas:
- httpx: Cliente HTTP assíncrono para fazer requisições à API da CoinGecko.
- Redis (via redis.asyncio): Para cache e armazenamento de dados em memória.
- dotenv: Para carregar variáveis de ambiente de forma segura.
"""

import logging
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

# httpx: Cliente HTTP assíncrono de terceiros para fazer requisições web.
import httpx
# load_dotenv: Função para carregar variáveis de ambiente de um arquivo .env.
from dotenv import load_dotenv
# aioredis: Cliente Redis assíncrono para Python.
import redis.asyncio as aioredis

# Configuração de logging:
# Configura o sistema de log para este script, direcionando para a saída padrão e um arquivo.
logging.basicConfig(
    level=logging.INFO, # Define o nível mínimo de mensagens a serem registradas (INFO, WARNING, ERROR, etc.).
    format='%(asctime)s - ETL - %(levelname)s - %(message)s', # Formato das mensagens de log.
    handlers=[ # Destinos onde as mensagens de log serão enviadas.
        logging.StreamHandler(), # Envia logs para a saída padrão (console/terminal).
        logging.FileHandler('etl.log', mode='a') # Envia logs para o arquivo 'etl.log', adicionando (append) ao final.
    ]
)
logger = logging.getLogger(__name__) # Cria um logger específico para este módulo.

# --- Carregamento de Variáveis de Ambiente ---
# Carrega as variáveis de ambiente do arquivo .env localizado na raiz do projeto.
# O Path(__file__).parent.parent constrói o caminho para a raiz do projeto.
load_dotenv(Path(__file__).parent.parent / '.env')
logger.info("✅ Variáveis de ambiente carregadas do arquivo .env na raiz do projeto.")

# --- Configurações e Parâmetros do Processo ETL ---
# Obtém variáveis de ambiente, com valores padrão caso não estejam definidas.
# REDIS_URL: URL de conexão com o servidor Redis, para cache e armazenamento.
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
# COINGECKO_API_KEY: Chave da API do CoinGecko, para acesso a dados premium (opcional).
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
# UPDATE_INTERVAL: Intervalo em segundos entre cada ciclo de atualização ETL (padrão: 5 minutos).
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '300'))
# Prefixo para as chaves no Redis
REDIS_KEY_PREFIX = 'crypto:'
# Nome da chave para estatísticas de mercado agregadas
MARKET_STATS_KEY = f"{REDIS_KEY_PREFIX}market:stats"

# URL base da API CoinGecko.
API_BASE_URL = "https://api.coingecko.com/api/v3"
# Tempo máximo em segundos para uma requisição HTTP.
REQUEST_TIMEOUT = 30
# Número máximo de tentativas de retry para requisições com falha.
MAX_RETRIES = 5
# Atraso inicial em segundos antes de uma nova tentativa (com backoff exponencial).
RETRY_DELAY = 10
# Tamanho do lote de registros a serem inseridos/atualizados no banco de dados por vez.
BATCH_SIZE = 100
# Atraso em segundos entre requisições consecutivas à API CoinGecko para respeitar limites de taxa.
RATE_LIMIT_DELAY = 1.2

# --- Inicialização do Cliente Redis ---
# Instância do cliente Redis, inicializada como None e configurada posteriormente.
redis_client: Optional[aioredis.Redis] = None


class CryptoDataUpdater:
    """
    Classe principal para gerenciar o processo ETL (Extração, Transformação, Carga)
    de dados de criptomoedas. Encapsula toda a lógica de coleta, processamento
    e persistência de dados.
    """

    def __init__(self):
        """
        Inicializa o CryptoDataUpdater.
        
        Configura o cliente HTTP assíncrono (httpx) para fazer requisições à CoinGecko,
        definindo timeout e cabeçalhos personalizados. Também inicializa um dicionário
        para armazenar métricas de performance do ETL.
        """
        # Cliente HTTP assíncrono para requisições externas, com timeout e headers.
        self.client = httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            headers={
                'User-Agent': 'CryptoDash-ETL/2.0', # Identifica o cliente para a API externa.
                'Accept': 'application/json',
                'X-Requested-With': 'CryptoDash ETL Process' # Identificador da requisição.
            }
        )
        self.last_update: Optional[datetime] = None # Armazena o timestamp da última atualização bem-sucedida.
        self.stats: Dict[str, Any] = { # Dicionário para coletar métricas de performance.
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_records_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    async def init_redis(self) -> None:
        """
        Inicializa a conexão com o servidor Redis para ser usado como cache.
        
        Tenta conectar ao Redis usando a URL configurada. Se a conexão falhar,
        registra um aviso e desativa o uso do cache para o restante da execução.
        """
        global redis_client # Acessa a variável global redis_client.
        try:
            # Cria uma instância do cliente Redis assíncrono.
            redis_client = aioredis.from_url(REDIS_URL, decode_responses=True) # decode_responses para obter strings.
            await redis_client.ping() # Testa a conexão com um comando PING.
            logger.info("✅ Conexão com Redis estabelecida para cache do ETL.")
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível em {REDIS_URL}: {e}. Continuando o ETL SEM cache.")
            redis_client = None # Define como None para desativar o cache.

    async def get_cache(self, key: str) -> Optional[str]:
        """
        Tenta obter um valor do cache Redis usando uma chave específica.
        
        Args:
            key (str): A chave para buscar no cache.
            
        Returns:
            Optional[str]: O valor armazenado em string se encontrado e Redis estiver ativo, senão None.
        """
        if not redis_client: # Se o cliente Redis não está ativo, não há cache.
            return None
        try:
            # Retorna o valor associado à chave. Se a chave não existe, retorna None.
            return await redis_client.get(key)
        except Exception as e:
            logger.warning(f"Erro ao tentar ler do cache Redis (chave: {key}): {e}")
            return None

    async def set_cache(self, key: str, value: str, ttl: int = 300) -> None:
        """
        Armazena um valor no cache Redis com um tempo de vida (TTL).
        
        Args:
            key (str): A chave para armazenar o valor.
            value (str): O valor a ser armazenado.
            ttl (int): Tempo de vida do item no cache em segundos (padrão: 300s = 5 minutos).
        """
        if not redis_client: # Se o cliente Redis não está ativo, não armazena.
            return
        try:
            # Define a chave com um valor e um tempo de expiração (TTL).
            await redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Erro ao tentar salvar no cache Redis (chave: {key}): {e}")

    async def check_rate_limit(self) -> None:
        """
        Pausa a execução para respeitar o limite de taxa (rate limit) da API CoinGecko.
        
        Um atraso é aplicado entre as requisições para evitar exceder o número de chamadas
        permitidas pela API em um determinado período.
        """
        await asyncio.sleep(RATE_LIMIT_DELAY) # Pausa por um tempo definido em RATE_LIMIT_DELAY.

    def validate_api_response(self, data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Valida a estrutura básica e o conteúdo da resposta recebida da API CoinGecko.
        
        Verifica se a resposta não está vazia, é uma lista e se os primeiros itens
        contêm os campos obrigatórios esperados.
        
        Args:
            data (List[Dict[str, Any]]): A lista de dados brutos recebidos da API.
            
        Returns:
            Tuple[bool, str]: Um booleano indicando se a validação foi bem-sucedida e
                              uma mensagem de status ou erro.
        """
        if not data: # Verifica se a lista de dados está vazia.
            return False, "Resposta vazia da API"

        if not isinstance(data, list): # Verifica se o tipo de dado é uma lista.
            return False, "Formato de resposta inválido: esperado uma lista"

        # Campos que são essenciais para o processamento posterior.
        required_fields = ['id', 'symbol', 'name', 'current_price']
        # Valida apenas os primeiros 5 itens para uma verificação rápida de sanidade.
        for item in data[:5]: 
            if not all(field in item for field in required_fields): # Verifica se todos os campos obrigatórios estão presentes.
                return False, f"Campos obrigatórios ausentes em um item da API: {required_fields}"

        return True, "Validação OK" # Se tudo estiver certo, a validação é bem-sucedida.

    async def fetch_crypto_data(self) -> List[Dict[str, Any]]:
        """
        🔍 FASE 1: EXTRAÇÃO - Busca dados de criptomoedas da API CoinGecko com estratégia de cache e retries.
        
        Tenta obter os dados do cache Redis primeiro. Se não estiverem no cache (cache miss),
        realiza uma requisição à API CoinGecko, aplicando um limite de taxa e lógica de retry
        com backoff exponencial para garantir robustez contra falhas de rede ou limites da API.
        
        Returns:
            List[Dict[str, Any]]: Uma lista de dicionários contendo os dados brutos das criptomoedas.
                                  Retorna uma lista vazia em caso de falha crítica.
        """
        cache_key = "crypto_data_latest" # Chave para armazenar os dados mais recentes no cache.
        start_time = datetime.utcnow() # Registra o tempo de início da extração para métricas.

        # 1. Tenta buscar dados do cache Redis:
        cached_data = await self.get_cache(cache_key)
        if cached_data: # Se os dados foram encontrados no cache...
            logger.info("📋 Dados de criptomoedas obtidos do cache Redis.")
            self.stats['cache_hits'] += 1 # Incrementa o contador de cache hits.
            return json.loads(cached_data) # Retorna os dados desserializados do JSON.

        # 2. Se os dados não estão no cache (cache miss), busca na API CoinGecko:
        logger.info("🌐 Dados de criptomoedas não encontrados no cache. Buscando frescos da API CoinGecko...")
        self.stats['cache_misses'] += 1 # Incrementa o contador de cache misses.

        # Parâmetros da requisição para a API CoinGecko.
        params = {
            'vs_currency': 'usd', # Moeda de comparação (USD).
            'order': 'market_cap_desc', # Ordenar por capitalização de mercado decrescente.
            'per_page': 250, # Número de resultados por página.
            'page': 1, # Primeira página de resultados.
            'sparkline': False, # Não incluir dados de sparkline.
            'price_change_percentage': '24h,7d,30d', # Incluir variação de preço para 24h, 7d e 30d.
            'market_data': True, # Incluir dados de mercado.
            'community_data': False, # Não incluir dados de comunidade.
            'developer_data': False # Não incluir dados de desenvolvedores.
        }

        # Se uma chave de API do CoinGecko for fornecida, usa-a para acesso premium.
        if COINGECKO_API_KEY:
            params['x_cg_demo_api_key'] = COINGECKO_API_KEY # Parâmetro específico para a API CoinGecko.
            logger.info("🔑 Usando API key do CoinGecko para acessar dados premium.")

        try:
            # Implementa a lógica de retry com backoff exponencial para maior robustez.
            for attempt in range(MAX_RETRIES): # Tenta um número máximo de vezes.
                try:
                    await self.check_rate_limit() # Respeita o rate limit antes de cada requisição.

                    # Faz a requisição GET para o endpoint de mercados de moedas.
                    response = await self.client.get(
                        f"{API_BASE_URL}/coins/markets",
                        params=params
                    )
                    response.raise_for_status() # Levanta um HTTPStatusError para respostas 4xx/5xx.
                    data = response.json() # Desserializa a resposta JSON.

                    # Valida a estrutura da resposta da API.
                    is_valid, validation_msg = self.validate_api_response(data)
                    if not is_valid: # Se a validação falhar, levanta um ValueError.
                        raise ValueError(f"Validação da resposta da API falhou: {validation_msg}")

                    # 3. Armazena os dados extraídos no cache Redis por 5 minutos.
                    await self.set_cache(cache_key, json.dumps(data), 300)

                    elapsed = (datetime.utcnow() - start_time).total_seconds() # Tempo total de extração.
                    logger.info(f"✅ Extração de dados concluída: {len(data)} registros em {elapsed:.2f} segundos.")
                    self.stats['successful_requests'] += 1 # Incrementa requisições bem-sucedidas.
                    self.stats['total_requests'] += 1 # Incrementa o total de requisições.

                    return data # Retorna os dados extraídos.

                except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as e: # Captura erros de HTTP, requisição ou validação.
                    self.stats['failed_requests'] += 1 # Incrementa requisições falhas.
                    if attempt == MAX_RETRIES - 1: # Se for a última tentativa, re-levanta o erro.
                        raise

                    delay = RETRY_DELAY * (2 ** attempt) # Calcula o atraso usando backoff exponencial.
                    logger.warning(
                        f"❌ Tentativa {attempt + 1}/{MAX_RETRIES} de extração falhou: {e}. "
                        f"Nova tentativa em {delay:.1f} segundos..."
                    )
                    await asyncio.sleep(delay) # Aguarda antes de tentar novamente.

        except Exception as e:
            logger.error(f"💥 Erro crítico e irrecuperável na fase de EXTRAÇÃO: {str(e)}", exc_info=True)
            raise # Re-levanta o erro crítico.
            
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        🛠️ FASE 2: TRANSFORMAÇÃO - Processa, valida e limpa os dados brutos de criptomoedas.
        
        Itera sobre a lista de dados brutos, aplicando validações essenciais, limpando
        e normalizando os valores (ex: convertendo para float, formatando strings).
        Adiciona metadados de processamento e calcula um score de qualidade para cada item.
        
        Args:
            data (List[Dict[str, Any]]): A lista de dicionários com os dados brutos da API.
            
        Returns:
            List[Dict[str, Any]]: Uma lista de dicionários com os dados transformados e prontos para a carga.
        """
        logger.info(f"🔄 Iniciando transformação de {len(data)} registros...")
        start_time = datetime.utcnow() # Registra o tempo de início da transformação.

        transformed_data = [] # Lista para armazenar os dados transformados.
        errors = [] # Lista para registrar quaisquer erros durante a transformação.

        for i, item in enumerate(data): # Itera sobre cada item nos dados brutos.
            try:
                # 1. Validação de dados essenciais para cada item.
                if not self._validate_crypto_item(item): # Usa um método auxiliar para validação.
                    errors.append(f"Item {i} (ID: {item.get('id', 'N/A')}): dados inválidos ou incompletos.")
                    continue # Pula para o próximo item se a validação falhar.

                # 2. Limpeza e normalização dos dados.
                clean_item = self._clean_crypto_data(item) # Usa um método auxiliar para limpeza.

                # 3. Adiciona metadados de processamento ao item transformado.
                clean_item.update({
                    'last_updated_from_api': item.get('last_updated'), # Timestamp original da API, se disponível.
                    'processed_at': datetime.utcnow().isoformat() + 'Z', # Timestamp de quando foi processado.
                    'data_quality_score': self._calculate_quality_score(item) # Score de qualidade dos dados.
                })

                transformed_data.append(clean_item) # Adiciona o item transformado à lista.

            except Exception as e:
                # Captura e registra erros específicos de transformação de um item.
                errors.append(f"Item {i} (ID: {item.get('id', 'N/A')}): erro de processamento - {str(e)}")
                logger.warning(f"⚠️ Erro processando item {i} (ID: {item.get('id', 'N/A')}): {e}")

        # 4. Log de estatísticas da transformação.
        elapsed = (datetime.utcnow() - start_time).total_seconds() # Tempo total da transformação.
        success_rate = (len(transformed_data) / len(data)) * 100 if data else 0 # Taxa de sucesso.

        logger.info(
            f"✅ Transformação concluída: {len(transformed_data)}/{len(data)} registros válidos "
            f"({success_rate:.1f}%) em {elapsed:.2f} segundos."
        )

        if errors:
            logger.warning(f"⚠️ Foram encontrados {len(errors)} erros durante a transformação. Primeiros 5: {errors[:5]}...")

        return transformed_data # Retorna a lista de dados transformados.

    def _validate_crypto_item(self, item: Dict[str, Any]) -> bool:
        """
        Método auxiliar para validar se um item de criptomoeda possui os campos obrigatórios.
        
        Args:
            item (Dict[str, Any]): O dicionário representando um item de criptomoeda.
            
        Returns:
            bool: True se todos os campos obrigatórios estiverem presentes e não forem None, False caso contrário.
        """
        required_fields = ['id', 'symbol', 'name', 'current_price'] # Campos que devem existir.
        return all(item.get(field) is not None for field in required_fields) # Verifica se todos estão presentes e não nulos.

    def _clean_crypto_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método auxiliar para limpar, normalizar e mapear os dados de criptomoeda.
        
        Converte tipos de dados (strings para floats/ints com segurança), padroniza
        valores (ex: minúsculas para símbolo/ID) e seleciona os campos relevantes
        para o esquema do banco de dados.
        
        Args:
            item (Dict[str, Any]): O dicionário de dados brutos de uma criptomoeda.
            
        Returns:
            Dict[str, Any]: Um novo dicionário com os dados limpos e formatados.
        """
        # Funções auxiliares para conversão segura de tipos numéricos.
        def safe_float(value, default=0.0): # Converte para float, retorna default em caso de erro.
            if value is None or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0): # Converte para int, com cuidado para floats, retorna default em caso de erro.
            if value is None or value == '':
                return default
            try:
                # Tenta converter para float primeiro para lidar com números como "123.0", depois para int.
                return int(float(value)) if '.' not in str(value) else default
            except (ValueError, TypeError):
                return default

        # Retorna um dicionário com os dados mapeados e limpos para o esquema final.
        return {
            'id': str(item.get('id', '')).lower(), # ID da criptomoeda em minúsculas.
            'symbol': str(item.get('symbol', '')).lower(), # Símbolo em minúsculas.
            'name': str(item.get('name', '')).strip(), # Nome, remove espaços extras.
            'price': safe_float(item.get('current_price'), 0.0), # Preço atual.
            'market_cap': safe_float(item.get('market_cap')), # Capitalização de mercado.
            'volume_24h': safe_float(item.get('total_volume')), # Volume de 24h.
            'change_24h': safe_float(item.get('price_change_percentage_24h')) / 100,  # Variação % de 24h (convertida para decimal).
            'last_updated': datetime.utcnow().isoformat() + 'Z', # Timestamp da última atualização (no script).

            # Campos adicionais de dados, limpos e formatados.
            'high_24h': safe_float(item.get('high_24h')),
            'low_24h': safe_float(item.get('low_24h')),
            'price_change_24h': safe_float(item.get('price_change_24h')),
            'market_cap_change_24h': safe_float(item.get('market_cap_change_24h')),
            'market_cap_change_percentage_24h': safe_float(item.get('market_cap_change_percentage_24h')),
            'circulating_supply': safe_float(item.get('circulating_supply')),
            'total_supply': safe_float(item.get('total_supply')),
            'max_supply': safe_float(item.get('max_supply')),

            # Dados de ATH (All-Time High) / ATL (All-Time Low).
            'ath': safe_float(item.get('ath')),
            'ath_change_percentage': safe_float(item.get('ath_change_percentage')),
            'ath_date': item.get('ath_date'),
            'atl': safe_float(item.get('atl')),
            'atl_change_percentage': safe_float(item.get('atl_change_percentage')),
            'atl_date': item.get('atl_date'),

            # Metadados adicionais.
            'image_url': str(item.get('image', '')).strip(), # URL da imagem, remove espaços.
            'market_cap_rank': safe_int(item.get('market_cap_rank')), # Rank de capitalização de mercado.
            'roi': item.get('roi'),  # Retorna ROI como está (pode ser JSON ou None).
        }

    def _calculate_quality_score(self, item: Dict[str, Any]) -> float:
        """
        Método auxiliar para calcular um score de qualidade para um item de dados.
        
        Atribui um score inicial de 100 e subtrai pontos para cada campo essencial
        que está ausente ou é nulo, dando uma indicação da completude e qualidade dos dados.
        
        Args:
            item (Dict[str, Any]): O dicionário de dados de uma criptomoeda.
            
        Returns:
            float: Um score de qualidade entre 0 e 100.
        """
        score = 100.0 # Score inicial máximo.
        # Define os campos a serem verificados e seu 'peso' na redução do score.
        checks = [
            ('current_price', 5),
            ('market_cap', 10),
            ('total_volume', 5),
            ('price_change_percentage_24h', 5),
            ('image', 2),
            ('market_cap_rank', 3),
        ]

        for field, weight in checks: # Itera sobre os campos e seus pesos.
            if not item.get(field): # Se o campo está ausente ou é None...
                score -= weight # ...reduz o score.

        return max(0, score) # Garante que o score não seja negativo.
    
    async def update_database(self, data: List[Dict[str, Any]]) -> None:
        """
        💾 FASE 3: ARMAZENAMENTO - Armazena os dados processados no Redis.
        
        Processa os dados em lotes e armazena no Redis, utilizando hashes para estruturar
        os dados de forma eficiente. Inclui lógica de retry para garantir a persistência 
        dos dados mesmo com falhas transitórias.
        
        Args:
            data (List[Dict[str, Any]]): Lista de dicionários com os dados de criptomoedas processados.
        """
        if not data:  # Se não houver dados para armazenar, sai da função.
            logger.warning("⚠️ Nenhum dado para armazenar no Redis.")
            return

        logger.info(f"💾 Iniciando armazenamento no Redis: {len(data)} registros...")
        start_time = datetime.utcnow()  # Registra o tempo de início do armazenamento.

        # Tamanho do lote para operações de armazenamento
        batch_size = 100
        total_batches = (len(data) + batch_size - 1) // batch_size
        success_count = 0
        failed_count = 0

        # Processa cada lote de dados
        for batch_num, i in enumerate(range(0, len(data), batch_size), 1):
            try:
                batch = data[i:i + batch_size]
                logger.info(f"🔄 Processando lote {batch_num}/{total_batches} ({len(batch)} registros)...")

                # Prepara os dados para armazenamento no Redis
                redis_data = {}
                for item in batch:
                    crypto_id = item.get('id')
                    if not crypto_id:
                        continue
                        
                    # Cria uma chave única para cada criptomoeda
                    key = f"{REDIS_KEY_PREFIX}price:{crypto_id.lower()}"
                    
                    # Prepara os dados para armazenamento
                    redis_data[key] = json.dumps({
                        'id': crypto_id,
                        'symbol': item.get('symbol', '').upper(),
                        'name': item.get('name', ''),
                        'current_price': item.get('current_price', 0),
                        'price_change_percentage_24h': item.get('price_change_percentage_24h', 0),
                        'market_cap': item.get('market_cap', 0),
                        'total_volume': item.get('total_volume', 0),
                        'image': item.get('image', ''),
                        'last_updated': item.get('last_updated', datetime.utcnow().isoformat()),
                        'high_24h': item.get('high_24h', 0),
                        'low_24h': item.get('low_24h', 0),
                        'price_change_24h': item.get('price_change_24h', 0),
                        'market_cap_change_24h': item.get('market_cap_change_24h', 0),
                        'market_cap_change_percentage_24h': item.get('market_cap_change_percentage_24h', 0),
                        'circulating_supply': item.get('circulating_supply', 0),
                        'total_supply': item.get('total_supply', 0),
                        'max_supply': item.get('max_supply', 0),
                        'ath': item.get('ath', 0),
                        'ath_change_percentage': item.get('ath_change_percentage', 0),
                        'ath_date': item.get('ath_date', ''),
                        'atl': item.get('atl', 0),
                        'atl_change_percentage': item.get('atl_change_percentage', 0),
                        'atl_date': item.get('atl_date', '')
                    })
                
                # Armazena os dados no Redis
                success = await self._store_in_redis(redis_data)
                
                if success:
                    success_count += len(batch)
                    logger.info(f"✅ Lote {batch_num} armazenado com sucesso no Redis.")
                else:
                    failed_count += len(batch)
                    logger.error(f"❌ Falha ao armazenar o lote {batch_num}/{total_batches} no Redis.")

                # Pequeno atraso entre lotes para não sobrecarregar o Redis
                if batch_num < total_batches:
                    await asyncio.sleep(0.1)

            except Exception as e:
                failed_count += len(batch)
                logger.error(f"❌ Erro inesperado ao processar o lote {batch_num}/{total_batches}: {e}", exc_info=True)

        # Calcula métricas de desempenho
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        success_rate = (success_count / len(data)) * 100 if data else 0

        logger.info("=" * 60)
        logger.info("📊 ESTATÍSTICAS DE ARMAZENAMENTO NO REDIS:")
        logger.info(f"   • Total de registros para armazenar: {len(data)}")
        logger.info(f"   • Lotes processados: {total_batches}")
        logger.info(f"   • Registros com sucesso: {success_count}")
        logger.info(f"   • Registros com falha: {failed_count}")
        logger.info(f"   • Taxa de sucesso: {success_rate:.2f}%")
        logger.info(f"   • Tempo total de processamento: {elapsed:.2f} segundos")
        logger.info(f"   • Performance média: {len(data)/elapsed:.1f} registros/segundo" if elapsed > 0 else "")
        logger.info("=" * 60)

        # Atualiza as estatísticas
        self.stats['total_records_processed'] += success_count
        self.stats['failed_requests'] += failed_count

    async def _store_in_redis(self, data: Dict[str, str]) -> bool:
        """
        Armazena os dados no Redis usando pipeline para melhor desempenho.
        
        Args:
            data (Dict[str, str]): Dicionário onde as chaves são as chaves do Redis
                                 e os valores são strings JSON com os dados a serem armazenados.
        
        Returns:
            bool: True se o armazenamento for bem-sucedido, False caso contrário.
        """
        if not redis_client:
            logger.error("❌ Cliente Redis não inicializado. Não foi possível armazenar os dados.")
            return False
            
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Cria um pipeline para executar múltiplos comandos em uma única operação
                async with redis_client.pipeline(transaction=True) as pipe:
                    for key, value in data.items():
                        # Define o valor e o tempo de expiração (1 hora)
                        pipe.set(key, value, ex=3600)
                    
                    # Executa o pipeline
                    await pipe.execute()
                
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:  # Última tentativa
                    logger.error(f"❌ Falha ao armazenar dados no Redis após {max_retries} tentativas: {e}", exc_info=True)
                    return False
                    
                # Backoff exponencial
                delay = base_delay * (2 ** attempt)
                logger.warning(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou. Nova tentativa em {delay:.1f}s...")
                await asyncio.sleep(delay)
        
        return False

    
    async def run_update(self) -> None:
        """
        🚀 Executa um ciclo completo do processo ETL (Extração, Transformação, Carga).
        
        Orquestra as três fases principais do ETL, registra métricas de tempo e processamento,
        e trata exceções críticas que possam ocorrer durante qualquer fase.
        
        Raises:
            Exception: Re-levanta qualquer erro crítico que impeça o ETL de continuar.
        """
        start_time = datetime.utcnow() # Registra o tempo de início do ciclo ETL.
        logger.info("🎯 Iniciando um ciclo completo do processo ETL...")

        try:
            # --- FASE 1: EXTRAÇÃO ---
            logger.info("📥 === INICIANDO FASE 1: EXTRAÇÃO DE DADOS ===")
            data = await self.fetch_crypto_data() # Chama o método de extração.

            if not data: # Se a extração não retornou dados, encerra o ciclo.
                logger.warning("⚠️ NENHUM DADO RETORNADO DA API. Encerrando ciclo ETL.")
                return

            # --- FASE 2: TRANSFORMAÇÃO ---
            logger.info("🔄 === INICIANDO FASE 2: TRANSFORMAÇÃO DE DADOS ===")
            transformed_data = self.transform_data(data) # Chama o método de transformação.

            if not transformed_data: # Se a transformação não resultou em dados válidos, encerra.
                logger.error("❌ FALHA NA TRANSFORMAÇÃO: Nenhum dado válido após o processamento. Encerrando ciclo ETL.")
                return

            # --- FASE 3: CARGA ---
            logger.info("💾 === INICIANDO FASE 3: CARGA DE DADOS NO SUPABASE ===")
            await self.update_database(transformed_data) # Chama o método de carga.

            # --- ATUALIZAÇÃO DE ESTATÍSTICAS GLOBAIS DE MERCADO ---
            # Este método calcula e insere estatísticas agregadas em uma tabela separada.
            logger.info("📊 Atualizando estatísticas globais de mercado...")
            await self.update_market_stats(data) # Usa os dados brutos para calcular estatísticas.

            # --- MÉTRICAS FINAIS DO CICLO ETL ---
            total_time = (datetime.utcnow() - start_time).total_seconds() # Tempo total do ciclo.

            logger.info("🎉 === CICLO ETL CONCLUÍDO COM SUCESSO ===")
            logger.info(f"⏱️ Tempo total do ciclo ETL: {total_time:.2f} segundos")
            logger.info(f"📊 Taxa de processamento: {len(transformed_data)/total_time:.1f} registros/segundo")
            logger.info(f"🎯 Eficiência: {len(transformed_data)/len(data)*100:.1f}% dos dados originais processados.")

            # Registra todas as métricas de performance acumuladas.
            self.log_performance_metrics()

        except Exception as e: # Captura qualquer erro crítico no processo ETL.
            logger.error(f"💥 Erro crítico no processo ETL: {str(e)}", exc_info=True)
            raise # Re-levanta o erro para tratamento externo, se houver.

    async def update_market_stats(self, data: List[Dict[str, Any]]) -> None:
        """
        📊 Atualiza estatísticas globais de mercado no banco de dados Supabase.
        
        Calcula métricas agregadas como capitalização de mercado total, volume de 24h,
        número de criptomoedas ativas e distribuição por capitalização. Essas estatísticas
        são então inseridas em uma tabela separada no Supabase.
        
        Args:
            data (List[Dict[str, Any]]): A lista de dicionários com os dados brutos das criptomoedas.
        """
        if not supabase_client: # Garante que o cliente Supabase esteja inicializado.
            logger.error("❌ Cliente Supabase não inicializado. Não foi possível atualizar as estatísticas de mercado.")
            return

        try:
            logger.info("🔄 Calculando e atualizando estatísticas globais de mercado...")

            # 1. Calcula estatísticas agregadas a partir dos dados extraídos.
            total_market_cap = sum(item.get('market_cap', 0) for item in data if item.get('market_cap'))
            total_volume_24h = sum(item.get('total_volume', 0) for item in data if item.get('total_volume'))
            active_cryptocurrencies = len([item for item in data if item.get('market_cap', 0) > 0])

            # 2. Calcula a distribuição de capitalização de mercado (exemplo).
            market_cap_distribution = {
                'large_cap': len([item for item in data if item.get('market_cap', 0) > 10000000000]),  # > $10 bilhões
                'mid_cap': len([item for item in data if 1000000000 < item.get('market_cap', 0) <= 10000000000]),  # $1 bilhão - $10 bilhões
                'small_cap': len([item for item in data if item.get('market_cap', 0) <= 1000000000])  # < $1 bilhão
            }

            # 3. Monta o dicionário de estatísticas de mercado.
            market_stats = {
                'timestamp': datetime.utcnow().isoformat() + 'Z', # Timestamp da atualização.
                'active_cryptocurrencies': active_cryptocurrencies, # Número de criptomoedas ativas.
                'total_market_cap_usd': total_market_cap, # Capitalização total de mercado.
                'total_volume_usd_24h': total_volume_24h, # Volume total em 24h.
                'market_cap_percentage': market_cap_distribution, # Distribuição de capitalização (JSON).
                'markets': 1  # Número de mercados (simulado, aqui é a API CoinGecko).
            }

            # 4. Insere as estatísticas na tabela 'market_stats' do Supabase.
            result = supabase_client.table('market_stats').insert(market_stats).execute()

            # Verifica se houve erro na operação de inserção.
            if hasattr(result, 'error') and result.error: # 'hasattr' é usado para verificar a existência de 'error'
                logger.warning(f"⚠️ Erro ao atualizar a tabela 'market_stats': {result.error}")
            else:
                logger.info("✅ Estatísticas globais de mercado atualizadas com sucesso.")

        except Exception as e: # Captura e registra qualquer erro durante a atualização das estatísticas.
            logger.warning(f"⚠️ Erro inesperado ao calcular/atualizar market_stats: {e}", exc_info=True)

    def log_performance_metrics(self) -> None:
        """
        📈 Log detalhado de métricas de performance acumuladas do ETL.
        
        Exibe no log um resumo das requisições, registros processados, cache hits e misses,
        oferecendo uma visão abrangente da eficiência do processo ETL ao longo de sua execução.
        """
        logger.info("📊 === MÉTRICAS DE PERFORMANCE ACUMULADAS DO ETL ===")
        logger.info(f"🔄 Total de requisições à API: {self.stats['total_requests']}")
        logger.info(f"✅ Requisições bem-sucedidas: {self.stats['successful_requests']}")
        logger.info(f"❌ Requisições com falha: {self.stats['failed_requests']}")
        # Calcula a taxa de sucesso das requisições, evitando divisão por zero.
        logger.info(f"📈 Taxa de sucesso das requisições: {self.stats['successful_requests']/max(self.stats['total_requests'],1)*100:.1f}%")
        logger.info(f"💾 Total de registros de criptomoedas processados e carregados: {self.stats['total_records_processed']}")
        logger.info(f"🎯 Cache hits (dados obtidos do Redis): {self.stats['cache_hits']}")
        logger.info(f"💭 Cache misses (dados buscados da API): {self.stats['cache_misses']}")
        logger.info("=" * 50)

    async def run_continuous(self) -> None:
        """
        🔄 Executa o processo ETL continuamente em um loop, com um intervalo configurável.
        
        Este é o modo de operação principal para manter os dados atualizados. Ele gerencia
        os ciclos de atualização, respeitando o intervalo definido e tratando interrupções
        (como Ctrl+C) e erros inesperados para garantir resiliência.
        """
        logger.info("🎯 Iniciando o serviço ETL em modo contínuo...")
        logger.info(f"⏰ O intervalo de atualização configurado é de {UPDATE_INTERVAL} segundos.")

        await self.init_redis() # Inicializa a conexão com o Redis no início do serviço contínuo.

        cycle_count = 0 # Contador para o número de ciclos ETL executados.

        while True: # Loop infinito para execução contínua.
            try:
                cycle_count += 1 # Incrementa o contador de ciclo.
                cycle_start = datetime.utcnow() # Registra o tempo de início do ciclo atual.

                logger.info(f"🔄 === INICIANDO CICLO ETL #{cycle_count} ===")

                await self.run_update() # Executa um ciclo completo de extração, transformação e carga.

                cycle_time = (datetime.utcnow() - cycle_start).total_seconds() # Calcula o tempo que o ciclo levou.

                # Calcula o tempo que o script deve 'dormir' até a próxima execução.
                # Garante que o intervalo entre as atualizações seja respeitado.
                sleep_time = max(0, UPDATE_INTERVAL - cycle_time)

                if sleep_time > 0: # Se o ciclo terminou antes do intervalo, espera.
                    logger.info(f"⏰ Próxima atualização em {sleep_time:.1f} segundos...")
                    await asyncio.sleep(sleep_time)
                else: # Se o ciclo demorou mais que o intervalo configurado.
                    logger.warning("⚠️ O ciclo ETL demorou mais que o intervalo configurado. A próxima atualização será imediata.")

            except asyncio.CancelledError: # Captura o erro quando o loop é cancelado (ex: por Ctrl+C).
                logger.info("🛑 Sinal de cancelamento recebido. Encerrando o serviço ETL contínuo...")
                break # Sai do loop.

            except Exception as e: # Captura qualquer erro inesperado no ciclo ETL.
                logger.error(f"💥 Erro inesperado no ciclo ETL #{cycle_count}: {str(e)}", exc_info=True)
                logger.info(f"🔄 Tentando novamente em {RETRY_DELAY} segundos após o erro...")
                await asyncio.sleep(RETRY_DELAY) # Aguarda antes de tentar novamente.

    async def close(self) -> None:
        """
        🧹 Fecha todos os recursos abertos pela classe CryptoDataUpdater.
        
        Garante que o cliente HTTP (httpx) e a conexão Redis sejam fechados
        de forma limpa ao final da execução do script, liberando recursos do sistema.
        """
        if self.client: # Fecha o cliente HTTP se estiver aberto.
            await self.client.aclose()
        if redis_client: # Fecha a conexão Redis se estiver ativa.
            await redis_client.close()
        logger.info("🧹 Todos os recursos de ETL foram liberados com sucesso.")


async def main():
    """
    🏃 Função principal que orquestra a execução do script ETL.
    
    Inicializa o `CryptoDataUpdater` e gerencia a execução do ETL em modo contínuo 
    ou de única atualização, tratando interrupções do usuário e erros fatais.
    """
    updater = CryptoDataUpdater() # Cria uma instância da classe principal do ETL.
    
    # Inicializa o cliente Redis
    await updater.init_redis()

    try:
        logger.info("🚀 === INICIANDO CRYPTO DASHBOARD ETL v2.0 ===")
        logger.info("📊 Sistema de extração, transformação e carga para monitoramento de criptomoedas.")
        logger.info("🛠️ Processo ETL robusto e otimizado.")

        # Decide se executa o ETL uma única vez ou em modo contínuo, baseado no UPDATE_INTERVAL.
        if UPDATE_INTERVAL <= 0: # Se o intervalo for 0 ou negativo, executa uma única vez.
            logger.info("Configurado para uma ÚNICA atualização de dados (UPDATE_INTERVAL <= 0).")
            await updater.run_update()
        else: # Se o intervalo for positivo, executa em modo contínuo.
            logger.info(f"Configurado para execução CONTÍNUA com intervalo de {UPDATE_INTERVAL} segundos.")
            await updater.run_continuous()

    except KeyboardInterrupt: # Captura a interrupção pelo teclado (Ctrl+C).
        logger.info("🛑 Interrupção pelo usuário (Ctrl+C) detectada. Iniciando o desligamento do serviço...")
    except Exception as e: # Captura qualquer exceção fatal não tratada.
        logger.critical(f"💥 ERRO FATAL E INESPERADO: {str(e)}. Encerrando o script com falha.", exc_info=True)
        sys.exit(1) # Sai do script com código de erro 1.
    finally:
        await updater.close() # Garante que os recursos sejam fechados independentemente do resultado.
        logger.info("✅ Serviço ETL encerrado com sucesso. Recursos liberados.")


if __name__ == "__main__":
    # Ponto de entrada do script. Executa a função 'main' de forma assíncrona.
    # asyncio.run() é usado para rodar funções assíncronas (async def) em Python.
    asyncio.run(main())
