# Autenticação com Render

Este documento descreve como configurar e usar o sistema de autenticação no painel de criptomoedas hospedado no Render.

## Configuração Inicial

1. **Configurar autenticação no Render**
   - Acesse o painel do Render em [https://dashboard.render.com/](https://dashboard.render.com/)
   - Navegue até as configurações do seu serviço
   - Configure as variáveis de ambiente necessárias para autenticação

2. **Variáveis de ambiente necessárias**
   Adicione as seguintes variáveis ao seu arquivo `.env`:
   ```
   RENDER_EXTERNAL_URL=sua_url_do_render
   NEXT_PUBLIC_API_BASE_URL=sua_url_da_api
   ```

## Implementação

### Frontend (Next.js)

1. **Instalar dependências**
   ```bash
   npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
   ```

2. **Configurar cliente Supabase**
   Crie um arquivo `lib/supabaseClient.js`:
   ```javascript
   import { createClient } from '@supabase/supabase-js'

   const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
   const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

   export const supabase = createClient(supabaseUrl, supabaseAnonKey)
   ```

3. **Proteger rotas**
   Use o componente `withAuth` para proteger rotas que requerem autenticação:
   ```javascript
   import { withAuth } from '@supabase/auth-helpers-nextjs'
   
   function Dashboard({ user }) {
     return (
       <div>
         <h1>Bem-vindo, {user.email}!</h1>
         {/* Conteúdo do dashboard */}
       </div>
     )
   }
   
   export const getServerSideProps = withAuth({ redirectTo: '/login' })
   
   export default Dashboard
   ```

### Backend (FastAPI)

1. **Instalar dependências**
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt] python-multipart
   ```

2. **Configurar autenticação**
   Crie um arquivo `backend/auth.py`:
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2PasswordBearer
   from jose import JWTError, jwt
   from datetime import datetime, timedelta
   from typing import Optional
   import os

   # Configurações
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = 30

   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

   def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
       to_encode = data.copy()
       if expires_delta:
           expire = datetime.utcnow() + expires_delta
       else:
           expire = datetime.utcnow() + timedelta(minutes=15)
       to_encode.update({"exp": expire})
       encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
       return encoded_jwt
   ```

## Fluxo de Autenticação

1. **Login**
   - O usuário insere email e senha
   - O frontend envia as credenciais para o endpoint de login do Supabase
   - Em caso de sucesso, o token JWT é armazenado no localStorage

2. **Acesso a rotas protegidas**
   - O token é enviado no cabeçalho Authorization
   - O backend valida o token antes de processar a requisição

3. **Logout**
   - Remove o token do localStorage
   - Invalida a sessão no Supabase

## Testes

Para testar a autenticação, você pode usar os testes automatizados:

```bash
# Testes de unidade
npm test

# Testes de integração
npm run test:integration
```

## Segurança

- Nunca exponha as chaves de API no frontend
- Use HTTPS em produção
- Implemente rate limiting
- Mantenha as dependências atualizadas
