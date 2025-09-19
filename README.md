# 📈 Painel de Criptomoedas com Supabase

## 🌟 Visão Geral

O Painel de Criptomoedas é uma aplicação web que fornece informações em tempo real sobre o mercado de criptomoedas, com foco em um processo ETL (Extração, Transformação e Carga) eficiente e otimizado.

### 🔄 Processo ETL (Extração, Transformação e Carga)

O coração do sistema é o processo ETL que garante dados atualizados e confiáveis:

1. **Extração (E)**
   - Coleta de dados da API CoinGecko
   - Frequência: Atualizações horárias (24x/dia)
   - Limite de requisições: Dentro da cota de 10.000/mês
   - Dados coletados: Preços, volumes, capitalização de mercado

2. **Transformação (T)**
   - Normalização dos dados para o formato padrão
   - Cálculo de métricas adicionais
   - Validação e limpeza dos dados
   - Agregação de informações relevantes

3. **Carga (L)**
   - Armazenamento otimizado no Supabase
   - Tabela `crypto_prices` para histórico completo
   - Visualização `latest_prices` para consultas rápidas
   - Atualização incremental para eficiência

### 🎯 Benefícios
- Dados sempre atualizados
- Uso eficiente da API (dentro dos limites)
- Desempenho otimizado para consultas frequentes
- Histórico completo para análise de tendências

Desenvolvido com uma arquitetura moderna, o projeto foi construído em fases, garantindo uma base sólida e escalável para atender às necessidades dos usuários.

## 🕒 Cronologia de Desenvolvimento

### 🏗️ Fase 1: Planejamento e Configuração Inicial

#### Objetivos:
- Definir a arquitetura do sistema
- Configurar o ambiente de desenvolvimento
- Estabelecer a estrutura do projeto

#### Realizações:
- [x] Configuração inicial do repositório Git
- [x] Definição da arquitetura (Frontend, Backend, Banco de Dados)
- [x] Configuração do ambiente de desenvolvimento
- [x] Criação da estrutura de diretórios

### 🔄 Fase 2: Desenvolvimento do Backend

#### Objetivos:
- Criar a API para fornecer dados às aplicações cliente
- Implementar a lógica de negócios
- Garantir segurança e desempenho

#### Realizações:
- [x] Configuração do FastAPI
- [x] Integração com a API CoinGecko
- [x] Implementação do cliente Supabase
- [x] Criação dos endpoints da API
- [x] Configuração do CORS
- [x] Implementação de cache para otimização

### 🎨 Fase 3: Desenvolvimento do Frontend

#### Objetivos:
- Criar uma interface de usuário intuitiva e responsiva
- Exibir dados de forma clara e acessível
- Garantir boa experiência do usuário

#### Realizações:
- [x] Configuração do Next.js com TypeScript
- [x] Implementação da interface com Tailwind CSS
- [x] Criação dos componentes principais
- [x] Integração com a API do backend
- [x] Implementação de gráficos interativos
- [x] Design responsivo para diferentes dispositivos

### 🔗 Fase 4: Integração e Testes

#### Objetivos:
- Garantir que todas as partes do sistema funcionem juntas
- Identificar e corrigir problemas
- Melhorar a qualidade do código

#### Realizações:
- [x] Testes de integração entre frontend e backend
- [x] Testes de desempenho
- [x] Correção de bugs
- [x] Melhorias na experiência do usuário
- [x] Otimização de desempenho

### 🚀 Fase 5: Implantação e Monitoramento

#### Objetivos:
- Disponibilizar a aplicação para os usuários
- Garantir disponibilidade e desempenho
- Monitorar o funcionamento

#### Realizações:
- [x] Configuração do ambiente de produção
- [x] Deploy na Vercel (frontend)
- [x] Deploy do backend (Render/Railway)
- [x] Configuração de domínio personalizado (rainersoft.com.br/crypto-dash)
- [x] Implementação de monitoramento
- [x] Configuração de atualizações automáticas

## 🛠️ Tecnologias Utilizadas

### Frontend
- **Framework**: Next.js 14
- **Linguagem**: TypeScript
- **Estilização**: Tailwind CSS
- **Gerenciamento de Estado**: React Query
- **Gráficos**: Chart.js

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth
- **Cache**: Redis (para otimização)

### Infraestrutura
- **Frontend**: Vercel
- **Backend**: Render/Railway
- **Banco de Dados**: Supabase
- **CI/CD**: GitHub Actions
- **Monitoramento**: Logs do Vercel e Supabase

## 🚀 Guia de Instalação e Uso


## 🚀 Guia de Configuração Rápida

### 1. Pré-requisitos

- [Node.js](https://nodejs.org/) 18+ (LTS recomendado)
- [Python](https://www.python.org/downloads/) 3.11+
- [Git](https://git-scm.com/)
- Conta no [Supabase](https://supabase.com/)
- Chave de API da [CoinGecko](https://www.coingecko.com/en/api)
- [Docker](https://www.docker.com/) (opcional, para execução com containers)

### 2. Configuração do Ambiente

1. **Clone o Repositório**
   ```bash
   git clone https://github.com/seu-usuario/crypto-dash-supabase.git
   cd crypto-dash-supabase
   ```

2. **Configuração do Supabase**
   - Crie um novo projeto em [Supabase](https://app.supabase.com/)
   - Acesse as configurações do projeto > API
   - Copie a URL e as chaves (anon e service_role)

3. **Configuração da API CoinGecko**
   - Acesse [CoinGecko API](https://www.coingecko.com/en/api)
   - Crie uma conta e gere uma chave de API
   - Limite gratuito: 50 chamadas/minuto, 10,000 chamadas/mês

4. **Arquivo de Ambiente**
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   # ========================
   # Configurações Gerais
   # ========================
   NODE_ENV=development
   DEBUG=true
   
   # ========================
   # Configurações do Supabase
   # ========================
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_ANON_KEY=sua_chave_anonima_do_supabase
   SUPABASE_SERVICE_ROLE_KEY=sua_chave_de_servico_do_supabase
   
   # ========================
   # Configurações da API
   # ========================
   # URL base da API (backend)
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   # Chave da API CoinGecko
   NEXT_PUBLIC_COINGECKO_API_KEY=sua_chave_da_api_coingecko
   
   # ========================
   # Configurações do Frontend
   # ========================
   NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
   NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
   
   # ========================
   # Configurações do Banco de Dados
   # ========================
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
   
   # ========================
   # Configurações de Cache (opcional)
   # ========================
   REDIS_URL=redis://localhost:6379
   CACHE_TTL=300  # 5 minutos
   ```

### 3. Configuração do Banco de Dados

1. **Migrações iniciais**
   ```bash
   # Navegue até o diretório do backend
   cd backend
   
   # Instale as dependências
   python -m pip install -r requirements.txt
   
   # Execute as migrações do banco de dados
   python -m alembic upgrade head
   ```

2. **Dados iniciais**
   ```bash
   # Execute o script para popular o banco com dados iniciais
   python scripts/seed_database.py
   ```

### 4. Iniciando os Serviços

#### Opção 1: Docker (Recomendado)

```bash
# Na raiz do projeto
docker-compose up --build
```

#### Opção 2: Execução Manual

1. **Backend**
   ```bash
   cd backend
   
   # Crie e ative o ambiente virtual
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   # Instale as dependências
   pip install -r requirements.txt
   
   # Inicie o servidor de desenvolvimento
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend**
   ```bash
   cd frontend
   
   # Instale as dependências
   npm install
   
   # Inicie o servidor de desenvolvimento
   npm run dev
   ```

### 5. Acessando a Aplicação

- **Frontend**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Banco de Dados (Supabase)**: Acesse o painel do Supabase

### 6. Configuração do ETL

O processo ETL é executado automaticamente a cada hora. Para executá-lo manualmente:

```bash
# Na raiz do projeto
python scripts/update_data.py
```

### 7. Configuração de Produção

Para implantação em produção, certifique-se de:

1. Atualizar as variáveis de ambiente para valores de produção
2. Configurar HTTPS
3. Configurar um servidor de banco de dados dedicado
4. Configurar monitoramento e logs
5. Configurar backup automático do banco de dados

   - API Docs: http://localhost:8000/docs

## 🏗️ Estrutura do Projeto

```
crypto-dash-supabase/
├── .github/
│   └── workflows/          # GitHub Actions para CI/CD
│       └── update-data.yml # Atualização automática de dados
│
├── backend/                # API FastAPI
│   ├── main.py            # Aplicação principal
│   ├── supabase_client.py  # Cliente Supabase
│   ├── requirements.txt    # Dependências Python
│   └── tests/             # Testes do backend
│
├── database/
│   └── schema.sql         # Esquema do banco de dados
│
├── frontend/              # Aplicação Next.js
│   ├── pages/            # Rotas da aplicação
│   │   ├── api/         # API Routes
│   │   ├── _app.tsx     # Configuração do app
│   │   └── index.tsx    # Página inicial
│   ├── src/
│   │   ├── components/  # Componentes reutilizáveis
│   │   ├── lib/        # Utilitários e configurações
│   │   └── styles/     # Estilos globais
│   └── public/         # Arquivos estáticos
│
├── scripts/             # Scripts utilitários
│   └── update_data.py  # Script de atualização de dados
│
├── .env.example        # Modelo de variáveis de ambiente
├── docker-compose.yml  # Configuração do Docker
└── README.md          # Este arquivo
```

### 🔄 Fluxo de Dados

1. **Atualização de Dados**
   - O GitHub Actions executa `scripts/update_data.py` a cada 15 minutos
   - Os dados são obtidos da API CoinGecko
   - Os dados processados são armazenados no Supabase

2. **Requisições do Usuário**
   - O frontend faz requisições para a API FastAPI
   - A API consulta o banco de dados Supabase
   - Os dados são retornados em formato JSON

## 📊 Atualizações e ETL

O sistema utiliza um processo de ETL (Extração, Transformação e Carga) para manter os dados atualizados de forma eficiente, respeitando os limites da API CoinGecko.

### 🔄 Atualizações Horárias
- **Frequência**: 1 chamada por hora × 24h = 24 chamadas/dia
- **Status**: ✅ Dentro do limite de 10.000 requisições/mês
- **Detalhes**: Atualizações regulares garantem dados sempre atualizados sem ultrapassar os limites da API

### 📊 Snapshot de Preços
- **Endpoint utilizado**: `/simple/price` ou `/coins/markets`
- **Dados coletados**:
  - Preço atual
  - Variação 24h
  - Volume de negociação
  - Capitalização de mercado
- **Status**: ✅ Implementado

### 🗃️ Armazenamento no Banco de Dados
- **Tabelas**:
  - `crypto_prices`: Histórico de preços
  - `latest_prices`: Últimos preços para consulta rápida
- **Status**: ✅ Implementado

### 🖥️ Interface do Usuário
- **Tecnologia**: Next.js com React
- **Características**:
  - Exibição em tempo real
  - Gráficos interativos
  - Atualizações automáticas
- **Status**: ✅ Implementado

### ⚙️ Backend FastAPI
- **Funções**:
  - Centralização das requisições à API
  - Processamento ETL eficiente
  - Cache de dados para reduzir chamadas à API
- **Status**: ✅ Implementado

### 🤖 Automação com GitHub Actions
- **Frequência**: Configurável (ex: a cada 15min ou 1h)
- **Vantagens**:
  - Atualizações programadas
  - Execução controlada
  - Logs de execução
- **Status**: ✅ Implementado

## 📁 Estrutura do Projeto

```
crypto-dash-supabase/
├── backend/                 # Backend FastAPI
│   ├── main.py             # Aplicação principal
│   ├── supabase_client.py   # Cliente Supabase
│   └── requirements.txt     # Dependências Python
├── frontend/                # Frontend Next.js
│   ├── pages/              # Rotas da aplicação
│   │   ├── api/            # Rotas da API
│   │   ├── _app.tsx        # Configuração do app
│   │   └── index.tsx       # Página inicial
│   ├── src/
│   │   └── lib/
│   │       └── supabase.ts # Configuração do cliente Supabase
│   └── styles/             # Estilos globais
├── database/
│   └── schema.sql          # Esquema do banco de dados
└── .github/workflows/      # GitHub Actions
    └── update-data.yml     # Atualização de dados
```

## 🤝 Como Contribuir

1. Faça um Fork do repositório
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.

## 🙏 Agradecimentos

- [CoinGecko](https://www.coingecko.com/) pela API de criptomoedas
- [Supabase](https://supabase.com/) pelo backend como serviço
- [Next.js](https://nextjs.org/) e [FastAPI](https://fastapi.tiangolo.com/) pelas excelentes documentações
- [Tailwind CSS](https://tailwindcss.com/) pelo framework CSS utilitário

## 📞 Suporte

Encontrou um problema ou tem alguma dúvida? Por favor, abra uma [issue](https://github.com/seu-usuario/crypto-dash-supabase/issues).
