# Scripts de Atualização de Dados

Este diretório contém scripts utilitários para gerenciamento e atualização de dados do painel de criptomoedas.

## Scripts Disponíveis

### `update_data.py`

**Descrição**: 
Atualiza os dados das criptomoedas no banco de dados Supabase consultando a API CoinGecko.

**Funcionalidades**:
- Busca dados em tempo real das principais criptomoedas
- Atualiza o banco de dados Supabase com as informações mais recentes
- Gerencia erros e registra atividades

**Uso**:
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar o arquivo .env com suas credenciais

# Executar o script
python scripts/update_data.py
```

**Agendamento**:
Recomenda-se configurar este script para rodar periodicamente (ex: a cada 5 minutos) usando um agendador de tarefas como cron (Linux/Mac) ou Task Scheduler (Windows).

## Requisitos
- Python 3.8+
- Dependências listadas em `requirements.txt`
- Acesso à API CoinGecko
- Credenciais do Supabase configuradas no arquivo `.env`
