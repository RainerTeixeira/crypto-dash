"""
@file supabase_client.py
@brief Configura e inicializa os clientes Supabase para o backend.

Este módulo é responsável por carregar as variáveis de ambiente relacionadas ao Supabase
e criar instâncias dos clientes Supabase. Ele inicializa tanto o cliente público (com a ANON_KEY)
quanto o cliente de 'service role' (com a SERVICE_ROLE_KEY) para operações que requerem
maiores privilégios no banco de dados.
"""

import os
import logging
import sys
# Pathlib para manipulação de caminhos, embora menos usado com .env na raiz.
from typing import Optional
# create_client: Função para criar a instância do cliente Supabase.
# Client: Tipo que representa o cliente Supabase.
from supabase import create_client, Client
# load_dotenv: Função para carregar variáveis de ambiente de um arquivo .env.
# from dotenv import load_dotenv

# Configuração de logging:
# Define como as mensagens de log serão formatadas e onde serão exibidas.
logging.basicConfig(
    level=logging.INFO, # Nível de log INFO: mostra informações, avisos e erros.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Envia logs para a saída padrão (terminal).
    ]
)
logger = logging.getLogger(__name__) # Objeto logger para este módulo.

# Carrega as variáveis de ambiente do arquivo .env na raiz do projeto.
# Com a configuração de Docker Compose, o .env na raiz é o principal.
# load_dotenv(Path(__file__).parent.parent / '.env')
logger.info("Variáveis de ambiente carregadas (via Docker Compose ou ambiente).")

# --- Inicialização dos Clientes Supabase ---
# Bloco try-except para garantir que a aplicação não falhe completamente
# se as credenciais do Supabase estiverem faltando ou incorretas.
try:
    logger.info("Iniciando a configuração dos clientes Supabase...")

    # Obtém a URL e as chaves do Supabase das variáveis de ambiente.
    # É CRÍTICO que essas variáveis estejam definidas no seu arquivo .env.
    # SUPABASE_URL: URL do seu projeto Supabase.
    supabase_url: str = os.getenv("SUPABASE_URL")
    # SUPABASE_ANON_KEY: Chave pública (anon) para acesso de usuários não autenticados (RLS).
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY")
    # SUPABASE_SERVICE_ROLE_KEY: Chave de service role para acesso privilegiado (bypass RLS).
    # Usada para operações de backend como o ETL, que precisam de mais permissões (ex: ETL).
    supabase_service_role_key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Verifica se as chaves obrigatórias estão presentes.
    if not supabase_url or not supabase_anon_key:
        error_msg = ("ERRO CRÍTICO: SUPABASE_URL ou SUPABASE_ANON_KEY não encontradas.\n"
                     "Verifique se o arquivo .env na raiz está configurado corretamente.")
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Conectando ao Supabase em: {supabase_url}")

    # 1. Cria o cliente Supabase padrão (com a chave ANÔNIMA):
    # Este cliente é usado para operações que respeitam o Row Level Security (RLS).
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    logger.info("Cliente Supabase (anon key) inicializado.")

    # 2. Cria o cliente Supabase de Service Role (admin) se a chave estiver disponível:
    # Este cliente tem privilégios elevados e pode ignorar o RLS.
    # É usado principalmente para scripts de backend como o ETL, que precisam de acesso total.
    if supabase_service_role_key:
        supabase_admin: Client = create_client(supabase_url, supabase_service_role_key)
        logger.info("Cliente Supabase admin (service role key) inicializado.")
    else:
        # Se a chave de service role não estiver presente, o cliente admin é o mesmo que o padrão.
        # Isso pode ser útil em ambientes onde a chave de admin não é necessária ou não está configurada.
        supabase_admin = supabase
        logger.warning("SUPABASE_SERVICE_ROLE_KEY não encontrada. Cliente Supabase admin será igual ao cliente padrão.")

    # Testa a conexão com o Supabase:
    # Executa uma função RPC simples (como 'version') para verificar se a conexão está funcionando.
    try:
        # Para testar, garantimos que 'version' exista no seu banco de dados ou use outra RPC/tabela simples.
        supabase.rpc('version').execute()
        logger.info("Conexão com Supabase estabelecida e verificada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao verificar conexão com Supabase: {str(e)}", exc_info=True)
        # Relevanta a exceção, pois a falta de conexão com o Supabase é crítica para a API.
        raise 

    logger.info("Clientes Supabase configurados com sucesso.")

except Exception as e:
    error_msg = f"Falha crítica na inicialização dos clientes Supabase: {str(e)}"
    logger.critical(error_msg, exc_info=True) # Usa nível CRITICAL para erros que impedem o funcionamento.
    # Em caso de falha crítica, define os clientes como None e levanta a exceção.
    # Isso garante que a aplicação não tente usar clientes não inicializados.
    supabase = None
    supabase_admin = None
    raise # Levanta a exceção para que a aplicação falhe se não puder se conectar ao Supabase.
