# Script de Atualização de Dados de Criptomoedas
# Este script busca dados de criptomoedas da API CoinGecko e os armazena no banco de dados Supabase.

# Importações necessárias
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis de ambiente do arquivo .env
# Isso permite acessar as credenciais do Supabase de forma segura
load_dotenv()

# Inicializa as credenciais do Supabase a partir das variáveis de ambiente
# Essas variáveis devem ser configuradas no arquivo .env ou nas configurações do servidor
url: str = os.environ.get("SUPABASE_URL", "")
chave: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Verifica se as credenciais do Supabase foram fornecidas
if not url or not chave:
    raise ValueError("Por favor, defina as variáveis de ambiente SUPABASE_URL e SUPABASE_SERVICE_KEY")

# Cria o cliente do Supabase para interagir com o banco de dados
# O cliente será usado para realizar operações CRUD no banco de dados
supabase: Client = create_client(url, chave)

def buscar_dados_criptomoedas():
    """
    Busca dados de criptomoedas da API CoinGecko.
    
    Esta função faz uma requisição à API pública da CoinGecko para obter informações
    sobre as principais criptomoedas do mercado, incluindo preço, capitalização de mercado,
    volume de negociação e variação percentual nas últimas 24 horas.
    
    Returns:
        list or None: Lista de dicionários contendo os dados das criptomoedas ou None em caso de erro
    """
    # URL base da API CoinGecko para obter dados de mercado
    url = "https://api.coingecko.com/api/v3/coins/markets"
    
    # Parâmetros da requisição para a API
    parametros = {
        'vs_currency': 'usd',  # Moeda de referência: Dólar Americano
        'ids': 'bitcoin,ethereum,cardano,solana,ripple,polkadot,avalanche-2,dogecoin',  # IDs das criptomoedas desejadas
        'order': 'market_cap_desc',  # Ordena por capitalização de mercado em ordem decrescente
        'per_page': 10,  # Limita a 10 resultados por página
        'page': 1,  # Número da página
        'sparkline': False,  # Não inclui dados de sparkline (gráfico de linha)
        'price_change_percentage': '24h'  # Inclui a variação percentual nas últimas 24h
    }
    
    try:
        # Faz a requisição GET para a API
        resposta = requests.get(url, params=parametros)
        # Verifica se houve erro na requisição
        resposta.raise_for_status()
        # Retorna os dados em formato JSON
        return resposta.json()
    except requests.exceptions.RequestException as erro:
        # Em caso de erro, exibe uma mensagem e retorna None
        print(f"Erro ao buscar dados da CoinGecko: {erro}")
        return None

def atualizar_banco_dados(dados):
    """
    Atualiza o banco de dados Supabase com os dados mais recentes das criptomoedas.
    
    Esta função recebe os dados das criptomoedas e os insere ou atualiza no banco de dados.
    Se uma criptomoeda já existir na tabela (com base no nome), seus dados serão atualizados.
    
    Args:
        dados (list): Lista de dicionários contendo os dados das criptomoedas
    """
    # Verifica se há dados para processar
    if not dados:
        print("Nenhum dado para atualizar.")
        return
    
    # Itera sobre cada criptomoeda nos dados recebidos
    for cripto in dados:
        # Prepara os dados para inserção/atualização no formato esperado pelo banco de dados
        dados_cripto = {
            'name': cripto['name'],  # Nome da criptomoeda
            'symbol': cripto['symbol'].upper(),  # Símbolo em letras maiúsculas
            'price': float(cripto['current_price']),  # Preço atual em USD
            'market_cap': cripto['market_cap'],  # Capitalização de mercado
            'volume_24h': cripto['total_volume'],  # Volume de negociação nas últimas 24h
            'change_24h': float(cripto['price_change_percentage_24h']),  # Variação percentual nas últimas 24h
            'last_updated': datetime.utcnow().isoformat(),  # Data/hora da última atualização
            'updated_at': datetime.utcnow().isoformat()  # Data/hora da última atualização (para controle interno)
        }
        
        try:
            # Usa a função upsert para inserir ou atualizar os dados
            # Se já existir um registro com o mesmo nome, ele será atualizado
            supabase.table('crypto_prices').upsert(
                dados_cripto,
                on_conflict='name'  # Define a coluna 'name' como chave para verificar duplicatas
            ).execute()
            print(f"Dados de {cripto['name']} atualizados com sucesso!")
        except Exception as erro:
            # Em caso de erro ao atualizar, exibe uma mensagem de erro
            print(f"Erro ao atualizar {cripto['name']}: {erro}")

def principal():
    """
    Função principal que orquestra o processo de atualização de dados.
    
    Esta função é o ponto de entrada do script e coordena as operações:
    1. Busca os dados mais recentes da API CoinGecko
    2. Atualiza o banco de dados com os dados obtidos
    """
    print("Iniciando atualização de dados de criptomoedas...")
    
    # 1. Busca os dados mais recentes da API CoinGecko
    dados_cripto = buscar_dados_criptomoedas()
    
    # 2. Se os dados foram obtidos com sucesso, atualiza o banco de dados
    if dados_cripto:
        atualizar_banco_dados(dados_cripto)
    
    print("Atualização concluída!")

# Ponto de entrada do script
# Verifica se o arquivo está sendo executado diretamente (não importado como módulo)
if __name__ == "__main__":
    principal()
