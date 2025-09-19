# Painel de Criptomoedas com Supabase

Um painel em tempo real de criptomoedas construído com Next.js, Supabase e FastAPI. Esta aplicação permite que os usuários acompanhem preços e dados de mercado de criptomoedas em tempo real.

## Funcionalidades

- Acompanhamento em tempo real de preços de criptomoedas
- Indicadores de variação de preço em 24 horas
- Design responsivo com Tailwind CSS
- Autenticação segura com Supabase
- Atualizações automáticas de dados via GitHub Actions

## Tecnologias Utilizadas

- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Banco de Dados**: Supabase (PostgreSQL)
- **Implantação**: Docker, GitHub Actions

## Pré-requisitos

- Node.js (versão 18 ou superior)
- Python (versão 3.11 ou superior)
- Docker (para conteinerização)
- Conta no Supabase

## Começando

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/crypto-dash-supabase.git
cd crypto-dash-supabase
```

### 2. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=sua_url_do_supabase
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua_chave_anonima_do_supabase
SUPABASE_SERVICE_KEY=sua_chave_de_servico_do_supabase

# API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Configure o Banco de Dados

1. Crie um novo projeto no Supabase
2. Execute o script SQL localizado em `database/schema.sql` no editor SQL do Supabase
3. Anote a URL e as chaves do seu projeto Supabase

### 4. Instale as Dependências

#### Frontend

```bash
cd frontend
npm install
```

#### Backend

```bash
cd ../backend
python -m venv venv
.\venv\Scripts\activate  # No Windows
pip install -r requirements.txt
```

### 5. Execute a Aplicação

#### Backend

```bash
cd backend
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm run dev
```

### 6. Acesse a Aplicação

Abra [http://localhost:3000](http://localhost:3000) no seu navegador.

## Implantação

### Docker

Construa e execute com Docker Compose:

```bash
docker-compose up --build
```

### GitHub Actions

O workflow em `.github/workflows/update-data.yml` está configurado para executar o script de atualização de dados a cada 15 minutos. Certifique-se de adicionar suas credenciais do Supabase aos segredos do repositório:

- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_SERVICE_KEY`: Chave de função de serviço do Supabase

## Estrutura do Projeto

```
crypto-dash-supabase/
├── backend/               # Backend FastAPI
│   ├── main.py           # Arquivo principal da aplicação
│   ├── supabase_client.py # Configuração do cliente Supabase
│   ├── requirements.txt  # Dependências Python
│   └── Dockerfile        # Configuração Docker para o backend
├── frontend/             # Frontend Next.js
│   ├── pages/            # Páginas da aplicação
│   ├── styles/           # Estilos globais
│   └── public/           # Arquivos estáticos
├── scripts/              # Scripts utilitários
│   └── update_data.py    # Script de atualização de dados
├── database/             # Esquema do banco de dados
│   └── schema.sql        # Definição do esquema SQL
└── .github/workflows/    # Workflows do GitHub Actions
    └── update-data.yml   # Workflow de atualização de dados
```

## Como Contribuir

1. Faça um Fork do repositório
2. Crie sua branch de feature (`git checkout -b feature/NovaFeature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona NovaFeature'`)
4. Faça push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.

## Agradecimentos

- [API CoinGecko](https://www.coingecko.com/pt/api) pelos dados de criptomoedas
- [Supabase](https://supabase.com/) pelos serviços de backend
- Documentação do [Next.js](https://nextjs.org/) e [FastAPI](https://fastapi.tiangolo.com/) documentation
