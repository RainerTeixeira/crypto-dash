# Configuração de Ambiente - Estrutura Organizada

## 📁 Estrutura de Arquivos de Ambiente

O projeto possui uma estrutura organizada de variáveis de ambiente, separando claramente as responsabilidades entre frontend e backend.

### Backend
- **Local:** `backend/.env`
- **Responsabilidade:** Variáveis específicas do servidor FastAPI
- **Variáveis incluem:**
  - `NODE_ENV` - Ambiente de execução (development/production)
  - `PORT` - Porta em que o servidor irá rodar (padrão: 8000)
  - `REDIS_URL` - URL de conexão com o Redis
  - `COINGECKO_API_KEY` - Chave da API do CoinGecko
  - `RENDER_EXTERNAL_URL` - URL externa do serviço no Render
  - `DATABASE_URL` - URL de conexão com o banco de dados

### Frontend
- **Local:** `frontend/.env.local`
- **Responsabilidade:** Variáveis específicas do Next.js/React
- **Variáveis incluem:**
  - `NEXT_PUBLIC_API_BASE_URL` - URL base da API do backend
  - `NEXT_PUBLIC_COINGECKO_API_KEY` - Chave da API do CoinGecko
  - `NEXT_PUBLIC_BASE_PATH` - Caminho base da aplicação
  - `RENDER_EXTERNAL_URL` - URL externa do serviço no Render

- **Local:** `.env` (apenas comentários)
- **Status:** Não utilizado - contém apenas documentação

## 🔄 Sistema de Carregamento Inteligente

O sistema de configuração detecta automaticamente o contexto de execução:

1. **Configuração Local**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   nano backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   nano frontend/.env.local
   ```

2. **No Render**
   - Acesse o painel do serviço
   - Vá em "Environment"
   - Adicione as variáveis de ambiente necessárias
   - Marque como sensíveis as que contêm informações confidenciais

3. **Variáveis de Exemplo**
   ```
   # Backend
   NODE_ENV=production
   PORT=8000
   REDIS_URL=redis://redis:6379/0
   COINGECKO_API_KEY=sua_chave_aqui
   RENDER_EXTERNAL_URL=sua_url_no_render
   
   # Frontend
   NEXT_PUBLIC_API_BASE_URL=sua_url_da_api
   NEXT_PUBLIC_BASE_PATH=/crypto-dash
   RENDER_EXTERNAL_URL=sua_url_no_render
   ```

## 🚀 Como Usar
### Backend
```bash
cd backend/
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend/
npm run dev
```

O sistema de carregamento de ambiente funcionará automaticamente em ambos os casos!
