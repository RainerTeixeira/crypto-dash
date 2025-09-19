from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o cliente Supabase
url: str = os.environ.get("SUPABASE_URL")
anon_key: str = os.environ.get("SUPABASE_ANON_KEY")
service_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Valida as variáveis de ambiente
if not all([url, anon_key, service_key]):
    missing = []
    if not url:
        missing.append("SUPABASE_URL")
    if not anon_key:
        missing.append("SUPABASE_ANON_KEY")
    if not service_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    raise ValueError(f"As seguintes variáveis de ambiente são necessárias: {', '.join(missing)}")

# Cria os clientes Supabase
supabase = create_client(url, anon_key)
supabase_admin = create_client(url, service_key)
