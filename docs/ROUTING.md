# 🛣️ Documentação do Sistema de Roteamento

Este documento descreve a estrutura de roteamento implementada no frontend Next.js do projeto Crypto Dashboard.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura de Rotas](#estrutura-de-rotas)
- [Redirecionamento](#redirecionamento)
- [SEO e Metadados](#seo-e-metadados)
- [Exemplos de Uso](#exemplos-de-uso)

## 🔍 Visão Geral

O sistema de roteamento foi implementado usando o roteamento baseado em arquivos do Next.js, oferecendo:

- **URLs Semânticas**: `/crypto-dash` como URL principal
- **Redirecionamento Automático**: `/` → `/crypto-dash`
- **SEO Otimizado**: Metadados específicos por página
- **Navegação Intuitiva**: Estrutura clara e organizada

## 🗂️ Estrutura de Rotas

```
frontend/src/pages/
├── index.tsx                    # Página de redirecionamento (/)
└── crypto-dash/
    └── index.tsx               # Dashboard principal (/crypto-dash)
```

### Mapeamento de URLs

| URL | Arquivo | Descrição |
|-----|---------|-----------|
| `/` | `pages/index.tsx` | Redirecionamento automático para `/crypto-dash` |
| `/crypto-dash` | `pages/crypto-dash/index.tsx` | Dashboard principal de criptomoedas |

## 🔄 Redirecionamento

### Implementação

O redirecionamento é implementado usando o hook `useRouter` do Next.js:

```typescript
// pages/index.tsx
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redireciona para /crypto-dash
    router.replace('/crypto-dash');
  }, [router]);

  return (
    <div>
      {/* Loading spinner enquanto redireciona */}
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-t-blue-500">
        Redirecionando para o dashboard...
      </div>
    </div>
  );
}
```

### Características

- **`router.replace()`**: Substitui a entrada atual no histórico (não adiciona nova entrada)
- **Loading State**: Exibe spinner durante o redirecionamento
- **SEO Friendly**: Meta tags apropriadas para a página de redirecionamento

## 🏷️ SEO e Metadados

### Página Principal (`/crypto-dash`)

```typescript
// pages/crypto-dash/index.tsx
export default function CryptoDashboard() {
  return (
    <MainLayout 
      title="Crypto Dashboard" 
      description="Dashboard de criptomoedas em tempo real com dados atualizados"
    >
      {/* Conteúdo do dashboard */}
    </MainLayout>
  );
}
```

### Metadados Gerados

```html
<head>
  <title>Crypto Dashboard</title>
  <meta name="description" content="Dashboard de criptomoedas em tempo real com dados atualizados" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="/favicon.ico" />
</head>
```

### Página de Redirecionamento (`/`)

```typescript
// pages/index.tsx
<Head>
  <title>Crypto Dashboard</title>
  <meta name="description" content="Dashboard de criptomoedas em tempo real" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="icon" href="/favicon.ico" />
</Head>
```

## 💡 Exemplos de Uso

### Navegação Programática

```typescript
import { useRouter } from 'next/router';

function NavigationComponent() {
  const router = useRouter();

  const goToDashboard = () => {
    router.push('/crypto-dash');
  };

  const goHome = () => {
    router.push('/');
  };

  return (
    <nav>
      <button onClick={goToDashboard}>Dashboard</button>
      <button onClick={goHome}>Home</button>
    </nav>
  );
}
```

### Links Estáticos

```typescript
import Link from 'next/link';

function NavigationLinks() {
  return (
    <nav>
      <Link href="/">
        <a>Home</a>
      </Link>
      <Link href="/crypto-dash">
        <a>Dashboard</a>
      </Link>
    </nav>
  );
}
```

### Verificação de Rota Atual

```typescript
import { useRouter } from 'next/router';

function ActiveLink() {
  const router = useRouter();
  const isDashboard = router.pathname === '/crypto-dash';

  return (
    <a 
      href="/crypto-dash"
      className={isDashboard ? 'active' : ''}
    >
      Dashboard
    </a>
  );
}
```

## 🔧 Configuração

### Next.js Config

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Configurações de base path se necessário
  // basePath: '/crypto-dash',
  // assetPrefix: '/crypto-dash/',
}

module.exports = nextConfig
```

### TypeScript

```typescript
// types/next.d.ts
import { NextPage } from 'next';

type AppPage = NextPage & {
  title?: string;
  description?: string;
};

// Uso nos componentes
const CryptoDashboard: AppPage = () => {
  // Componente
};

CryptoDashboard.title = 'Crypto Dashboard';
CryptoDashboard.description = 'Dashboard de criptomoedas em tempo real';
```

## 🚀 Extensões Futuras

### Estrutura de Rotas Expandida

```
frontend/src/pages/
├── index.tsx                    # Redirecionamento (/)
├── crypto-dash/
│   ├── index.tsx               # Dashboard principal (/crypto-dash)
│   ├── [id].tsx               # Detalhes da criptomoeda (/crypto-dash/bitcoin)
│   └── historico/
│       └── [id].tsx           # Histórico (/crypto-dash/historico/bitcoin)
├── sobre.tsx                   # Página sobre (/sobre)
└── api/
    └── health.ts              # Health check da API (/api/health)
```

### Implementação de Rotas Dinâmicas

```typescript
// pages/crypto-dash/[id].tsx
import { useRouter } from 'next/router';

export default function CryptoDetails() {
  const router = useRouter();
  const { id } = router.query; // 'bitcoin', 'ethereum', etc.

  return (
    <MainLayout title={`${id} - Detalhes`}>
      <h1>Detalhes da {id}</h1>
      {/* Conteúdo específico da criptomoeda */}
    </MainLayout>
  );
}
```

### Middleware de Roteamento

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Redirecionamento baseado em condições
  if (request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/crypto-dash', request.url));
  }
}

export const config = {
  matcher: ['/'],
};
```

## 📚 Referências

- [Next.js Routing Documentation](https://nextjs.org/docs/routing/introduction)
- [Next.js Router API](https://nextjs.org/docs/api-reference/next/router)
- [Next.js Link Component](https://nextjs.org/docs/api-reference/next/link)
- [Next.js Head Component](https://nextjs.org/docs/api-reference/next/head)
