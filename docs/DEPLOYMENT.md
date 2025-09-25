# 🚀 Guia de Deploy - Crypto Dashboard

Este documento fornece instruções detalhadas para fazer deploy do projeto Crypto Dashboard no Render.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Configuração do Repositório](#configuração-do-repositório)
- [Deploy na Vercel](#deploy-na-vercel)
- [Configuração de Variáveis de Ambiente](#configuração-de-variáveis-de-ambiente)
- [Configuração do Domínio](#configuração-do-domínio)
- [Verificação do Deploy](#verificação-do-deploy)
- [Troubleshooting](#troubleshooting)

## ✅ Pré-requisitos

### 1. Conta no Render

- [x] Conta criada no [Render](https://render.com)
- [x] Conta conectada ao GitHub ou GitLab

### 2. Repositório de Código

- [x] Repositório público ou privado no GitHub/GitLab
- [x] Código commitado e pushed

### 3. Configurações do Backend

- [x] Backend deployado e funcionando
- [x] URL da API disponível
- [x] Banco de dados configurado (se necessário)

## 🔧 Configuração do Repositório

### 1. Estrutura de Arquivos

Certifique-se de que a estrutura está correta:

```
crypto-dash-supabase/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── (dashboard)/
│   │   │       └── crypto-dash/
│   │   │           └── page.tsx
│   │   ├── components/
│   │   ├── lib/
│   │   └── ...
│   ├── next.config.js
│   ├── package.json
│   └── ...
├── vercel.json
└── ...
```

### 2. Arquivos de Configuração

### 1. Conectar Repositório

1. Acesse o [Dashboard do Render](https://dashboard.render.com/)
2. Clique em "New" e selecione "Web Service"
3. Conecte seu repositório do GitHub/GitLab
4. Selecione o repositório do projeto
5. Configure o serviço:
   - **Name**: crypto-dashboard
   - **Region**: Selecione a região mais próxima
   - **Branch**: main (ou a branch desejada)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `cd frontend && npm start`
   - **Environment**: Node
   - **Node Version**: 18.x (LTS)
6. Clique em "Create Web Service"

### 2. Configurações de Build

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "cd frontend && npm install"
}
```
## 🆘 Suporte

Em caso de problemas:

1. Verifique os logs de deploy
2. Teste localmente com as mesmas variáveis
3. Consulte a documentação da Vercel
4. Abra uma issue no repositório
