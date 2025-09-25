<div align="center">
  <h1>📊 Crypto Dashboard</h1>
  <p>Um painel de criptomoedas em tempo real construído com Next.js 14, FastAPI e Redis</p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Next.js](https://img.shields.io/badge/Next.js-14.0.0-black?logo=next.js)](https://nextjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-3178C6?logo=typescript)](https://www.typescriptlang.org/)
  [![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3.0-06B6D4?logo=tailwind-css)](https://tailwindcss.com/)
  [![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)

  [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Frainerteixeira%2Fcrypto-dash)
  [![Deploy with Render](https://render.com/images/deploy-to-render/button.svg)](https://render.com/deploy)
</div>

## 🌟 Visão Geral

O **Crypto Dashboard** é uma aplicação full-stack focada em **ETL (Extração, Transformação e Carga)** de dados de criptomoedas, utilizando exclusivamente a API do **CoinGecko** como fonte de dados. O pipeline ETL foi projetado para extrair, processar e disponibilizar dados de forma eficiente e confiável para análise e visualização em tempo real.

### 🚀 Pipeline ETL com CoinGecko

1. **Extração (E)**
   - Integração direta com a [API do CoinGecko](https://www.coingecko.com/en/api)
   - Coleta de dados em tempo real de cotações, volumes e capitalização de mercado
   - Suporte a múltiplas criptomoedas e pares de negociação
   - Coleta programada para manter os dados sempre atualizados

2. **Transformação (T)**
   - Limpeza e normalização dos dados brutos da API
   - Cálculo de indicadores técnicos baseados nos dados do CoinGecko
   - Processamento de séries temporais para análise de tendências
   - Validação e tratamento de erros específicos da API

3. **Carga (L)**
   - Armazenamento em cache distribuído com Redis
   - Atualização em tempo real dos dashboards via WebSockets
   - Geração de relatórios e alertas baseados nos dados processados
   - Cache inteligente para otimizar o uso da API do CoinGecko
   - Persistência de dados em memória para acesso rápido

### 📊 Visualização de Dados
Além do poderoso backend de processamento, o projeto oferece uma interface moderna e responsiva para visualização dos dados processados, com gráficos interativos e painéis personalizáveis.

## ✨ Recursos Principais

- 🚀 **Tempo Real**: Atualizações em tempo real dos preços das criptomoedas
- 📱 **Responsivo**: Design que se adapta a qualquer dispositivo
- 📊 **Gráficos Interativos**: Visualizações detalhadas do histórico de preços
- 🔔 **Alertas Personalizáveis**: Notificações quando os preços atingirem seus alvos
- 🌍 **Dados Globais**: Estatísticas abrangentes do mercado de criptomoedas

## 🏗️ Arquitetura

A arquitetura da aplicação foi projetada para desempenho e escalabilidade, utilizando os melhores serviços para cada camada:

### 🖥️ Frontend (Vercel)

| Tecnologia | Descrição |
|------------|-----------|
| **Framework** | Next.js 14 com App Router |
| **Linguagem** | TypeScript |
| **Estilização** | Tailwind CSS |
| **Gerenciamento de Estado** | React Hooks e Context API |
| **Testes** | Jest e React Testing Library |
| **Hospedagem** | Vercel |
| **Domínio** | Configuração personalizável |

### ⚙️ Backend (Render)

| Componente | Detalhes |
|------------|-----------|
| **Framework** | FastAPI (Python 3.11+) |
| **Hospedagem** | Render Web Service |
| **Banco de Dados** | PostgreSQL gerenciado |
| **Cache** | Redis para otimização |
| **Autenticação** | JWT (JSON Web Tokens) |
| **Documentação** | Swagger UI / ReDoc |
| **Escalabilidade** | Automática |

## 🌐 Infraestrutura

### Frontend (Vercel)
- 🚀 Hospedagem estática otimizada
- 🌍 CDN global para entrega rápida
- 🤖 Deploys automáticos com Git
- 🔄 Preview Deploys para cada PR

### Backend (Render)
- ⚡ Serviço Web escalável
- 💾 Banco de Dados PostgreSQL gerenciado
- 📊 Monitoramento integrado
- 🔄 Escalabilidade automática

### Integração
- 🔄 Comunicação via API REST
- 🔒 Autenticação JWT segura
- 🌐 CORS configurado para domínios específicos

## ✨ Funcionalidades

### Para Usuários
- 📊 Visualização em tempo real de preços de criptomoedas
- 📈 Gráficos interativos de histórico de preços
- 🔔 Alertas de preço personalizáveis
- 📱 Design responsivo para todos os dispositivos
- 🔄 Atualização automática de dados

### Para Desenvolvedores
- 🏗️ **Arquitetura Limpa**: Código modular e bem organizado
- 📚 **Documentação Completa**: Swagger UI integrado e guias detalhados
- 🧪 **Testes Automatizados**: Cobertura abrangente de testes
- 🔒 **Segurança**: Autenticação JWT e boas práticas de segurança
- 🐳 **Containerização**: Docker e Docker Compose prontos para uso
- 🔄 **CI/CD**: Pipeline de integração e deploy contínuo

## 📂 Estrutura do Projeto

```
crypto-dashboard/
├── backend/                      # API em FastAPI
│   ├── app/                      # Código-fonte da aplicação
│   │   ├── __init__.py
│   │   ├── main.py               # Configuração principal do FastAPI
│   │   ├── api/                  # Rotas da API
│   │   │   ├── v1/               # Versão 1 da API
│   │   │   │   ├── endpoints/    # Endpoints da API
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── core/                 # Lógica de negócios
│   │   │   ├── config.py         # Configurações da aplicação
│   │   │   └── security.py       # Configurações de segurança
│   │   ├── db/                   # Configuração do banco de dados
│   │   │   ├── base.py           # Classe base do banco
│   │   │   ├── session.py        # Sessão do banco
│   │   │   └── init_db.py        # Inicialização do banco
│   │   ├── models/               # Modelos de dados
│   │   │   ├── __init__.py
│   │   │   └── user.py           # Modelo de usuário
│   │   └── schemas/              # Esquemas Pydantic
│   │       └── user.py
│   ├── tests/                    # Testes automatizados
│   ├── requirements.txt          # Dependências Python
│   └── Dockerfile                # Configuração do container
│
├── frontend/                     # Aplicação Next.js
│   ├── public/                   # Arquivos estáticos
│   │   ├── images/               # Imagens do projeto
│   │   └── favicon.ico           # Ícone do site
│   └── src/
│       ├── app/                  # Rotas da aplicação (App Router)
│       │   ├── api/              # Rotas da API
│       │   ├── crypto-dash/      # Dashboard de criptomoedas
│       │   │   ├── page.tsx      # Página principal
│       │   │   └── components/   # Componentes específicos
│       │   ├── auth/             # Autenticação
│       │   ├── globals.css       # Estilos globais
│       │   └── layout.tsx        # Layout principal
│       │
│       ├── components/           # Componentes reutilizáveis
│       │   ├── ui/               # Componentes de interface
│       │   │   ├── button.tsx
│       │   │   ├── card.tsx
│       │   │   └── ...
│       │   └── crypto/           # Componentes específicos de cripto
│       │       ├── PriceChart.tsx
│       │       └── ...
│       │
│       ├── lib/                  # Bibliotecas e utilitários
│       │   ├── api/              # Clientes de API
│       │   │   └── client.ts     # Cliente HTTP
│       │   └── utils/            # Funções utilitárias
│       │       └── formatters.ts
│       │
│       └── styles/               # Estilos globais
│           └── globals.css
│
├── .github/                      # Configurações do GitHub
│   └── workflows/                # GitHub Actions
│       └── ci-cd.yml
│
├── scripts/                      # Scripts de automação
│   ├── setup.sh                  # Script de configuração
│   └── deploy.sh                 # Script de deploy
│
├── tests/                        # Testes automatizados
│   ├── unit/                     # Testes unitários
│   └── e2e/                      # Testes end-to-end
│
├── .env.example                  # Exemplo de variáveis de ambiente
├── docker-compose.yml            # Configuração dos serviços
├── package.json                  # Dependências do frontend
├── tsconfig.json                 # Configuração do TypeScript
└── README.md                     # Este arquivo
```

## 🚀 Começando

### 📋 Pré-requisitos

Antes de começar, verifique se você possui os seguintes requisitos instalados em sua máquina:

#### 🛠️ Ferramentas de Desenvolvimento
- [Node.js](https://nodejs.org/) 18+ e npm 9+
- [Python](https://www.python.org/downloads/) 3.11+
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) (opcional)

#### ☁️ Contas Necessárias
- [GitHub](https://github.com/) (para versionamento de código)
- [Vercel](https://vercel.com/) (para deploy do frontend)
- [Render](https://render.com/) (para deploy do backend)
- [Redis Cloud](https://redis.com/cloud/overview/) (para cache e armazenamento)
- [CoinGecko API](https://www.coingecko.com/en/api) (para dados de criptomoedas)

#### 🔑 Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example` e preencha as seguintes variáveis:

```env
# Backend
REDIS_URL=redis://localhost:6379
JWT_SECRET=sua_chave_secreta_muito_segura
COINGECKO_API_KEY=sua_chave_coingecko

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Configuração do Ambiente

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/crypto-dashboard.git
   cd crypto-dashboard
   ```

2. **Configure as variáveis de ambiente**
   Crie e configure os arquivos de ambiente:
   ```bash
   # Backend
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais do Render
   ```

3. **Opção 1: Desenvolvimento com Docker (Recomendado)**
   ```bash
   docker-compose up -d
   ```

4. **Opção 2: Desenvolvimento local**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # No Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   
   # Em outro terminal para o frontend
   cd frontend
   npm install
   npm run dev
   ```

5. **Acesse as aplicações**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API: [http://localhost:8000](http://localhost:8000)
   - Documentação da API: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🌐 Guia de Deploy

### 1. Backend no Render

1. **Banco de Dados**
   - Acesse o [Render Dashboard](https://dashboard.render.com/)
   - Crie um novo banco de dados PostgreSQL
   - Anote as credenciais fornecidas

2. **Deploy da API**
   - Crie um novo "Web Service" no Render
   - Conecte ao seu repositório GitHub
   - Configure as variáveis de ambiente:
     ```
     DATABASE_URL=postgresql://user:password@host:port/dbname
     JWT_SECRET=sua_chave_secreta
     COINGECKO_API_KEY=sua_chave_coingecko
     NODE_ENV=production
     PORT=8000
     CORS_ORIGINS=https://seu-frontend.vercel.app
     ```

### 2. Frontend na Vercel

1. **Importe o Projeto**
   - Acesse [Vercel Dashboard](https://vercel.com/dashboard)
   - Importe o repositório do GitHub
   - Configure as variáveis de ambiente:
     ```
     NEXT_PUBLIC_API_BASE_URL=https://seu-backend.onrender.com
     NEXT_PUBLIC_COINGECKO_API_KEY=sua_chave_coingecko
     ```

2. **Configurações de Build**
   - Framework: Next.js
   - Comando de build: `npm run build`
   - Diretório de saída: `.next`

### 3. Configuração de Domínio (Opcional)

1. **Vercel**
   - Configure um domínio personalizado
   - Habilite HTTPS automático

2. **Render**
   - Adicione o domínio personalizado
   - Configure o SSL

## 🛠️ Desenvolvimento

### Estrutura do Backend

O backend segue uma arquitetura limpa com separação clara de responsabilidades:

- **app/api/** - Endpoints da API organizados por domínio
- **app/core/** - Lógica de negócios e casos de uso
- **app/db/** - Configuração e migrações do banco de dados
- **app/models/** - Modelos Pydantic e SQLAlchemy
- **app/services/** - Serviços de domínio
- **app/utils/** - Utilitários e helpers

### Testes

```bash
# Testes do backend
cd backend
pytest

# Testes do frontend
cd frontend
npm test
```

### Deploy

O projeto está configurado para deploy contínuo no Render. Bushar para a branch `main` para acionar o pipeline de CI/CD.

1. Crie um novo serviço Web no Render
2. Conecte ao repositório do GitHub
3. Configure as variáveis de ambiente necessárias
4. Defina os comandos de build e start

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 📞 Contato

Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter)

Link do Projeto: [https://github.com/seu-usuario/crypto-dashboard](https://github.com/seu-usuario/crypto-dashboard)

## 🙌 Agradecimentos

- [CoinGecko API](https://www.coingecko.com/en/api) por fornecer os dados de criptomoedas
- [Next.js](https://nextjs.org/) e [FastAPI](https://fastapi.tiangolo.com/) pelas excelentes ferramentas
- A todos os contribuidores que ajudaram a melhorar este projeto
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
    "current_price": 50000,
    "price_change_percentage_24h": 2.5,
    "market_cap": 950000000000
  },
  ...
]
```

### GET /api/estatisticas
Retorna estatísticas gerais do mercado.

**Exemplo de resposta:**
```json
{
  "market_cap": 2500000000000,
  "volume_24h": 120000000000,
  "btc_dominance": 42.5,
  "active_cryptocurrencies": 12000,
  "last_updated": "2025-09-24T16:00:00Z"
}
```

## 🔄 Roteamento e Configuração

### Roteamento no Frontend

O frontend está configurado para funcionar no caminho `/crypto-dash` tanto em desenvolvimento quanto em produção. A navegação é feita através do App Router do Next.js 14.

### Variáveis de Ambiente

O projeto utiliza as seguintes variáveis de ambiente:

- `NEXT_PUBLIC_API_URL`: URL base da API do backend (ex: `http://localhost:8000`)
- `NEXT_PUBLIC_APP_NAME`: Nome da aplicação (opcional)
- `NEXT_PUBLIC_APP_DESCRIPTION`: Descrição da aplicação (opcional)

### Configuração do Next.js

O arquivo `next.config.js` contém configurações importantes como:
- Otimização de imagens
- Cabeçalhos de segurança
- Configurações de cache
- Redirecionamentos

## 📦 Estrutura de Dados

### Dados de Criptomoedas

O frontend espera receber um array de objetos com as seguintes propriedades:

```typescript
interface CryptoCurrency {
  id: string;            // Identificador único (ex: "bitcoin")
  symbol: string;         // Símbolo (ex: "btc")
  name: string;           // Nome completo (ex: "Bitcoin")
  image: string;          // URL da imagem do ícone
  current_price: number;  // Preço atual em USD
  price_change_percentage_24h: number;  // Variação percentual em 24h
  market_cap: number;     // Capitalização de mercado em USD
}
```

### Dados de Estatísticas

```typescript
interface MarketStats {
  market_cap: number;            // Capitalização total do mercado
  volume_24h: number;            // Volume total em 24h
  btc_dominance: number;         // Dominância do Bitcoin no mercado (%)
  active_cryptocurrencies: number; // Número total de criptomoedas ativas
  last_updated: string;          // Data/hora da última atualização (ISO 8601)
}
```

## 🛠️ Desenvolvimento

### Comandos Úteis

- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Gera uma versão de produção
- `npm start` - Inicia o servidor de produção (após o build)
- `npm run lint` - Executa o linter
- `npm run format` - Formata o código com Prettier
- `npm test` - Executa os testes automatizados

### Implantação

1. **Build para Produção**
   ```bash
   cd frontend
   npm run build
   ```

2. **Servindo a Aplicação**
   ```bash
   npm start
   ```

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para obter mais detalhes.

## 🙌 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## 🙋‍♂️ Suporte

Se precisar de ajuda ou tiver dúvidas, abra uma [issue](https://github.com/seu-usuario/crypto-dash-render/issues) no repositório.

A aplicação estará disponível em `http://localhost:3000/crypto-dash` por padrão.

## 📞 Contato

Para mais informações, entre em contato:

- Email: contato@rainersoft.com.br
- Site: [https://rainersoft.com.br](https://rainersoft.com.br)
- LinkedIn: [Rainer Teixeira](https://linkedin.com/in/rainerteixeira)
