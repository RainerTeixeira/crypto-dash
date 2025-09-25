// Configurações da aplicação
export const APP_CONFIG = {
  // Nome da aplicação
  name: 'Crypto Dashboard',
  
  // Descrição da aplicação
  description: 'Dashboard de Criptomoedas com Next.js e Render',
  
  // Configurações da API
  api: {
    // URL base da API - Usando a URL do backend
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    
    // Endpoints da API
    endpoints: {
      cryptocurrencies: '/criptomoedas',
      marketStats: '/estatisticas',
    },
    
    // Tempo máximo de espera para as requisições (em milissegundos)
    timeout: 10000,
  },
  
  // Configurações do Backend
  backend: {
    // URL base do backend hospedado no Render
    url: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  },
  
  // Configurações de cache
  cache: {
    // Tempo de expiração do cache em segundos
    ttl: 60, // 1 minuto
    
    // Chave para armazenar os dados em cache
    keys: {
      cryptocurrencies: 'cryptocurrencies',
      marketStats: 'marketStats',
    },
  },
  
  // Configurações de UI/UX
  ui: {
    // Número de itens por página
    itemsPerPage: 20,
    
    // Moeda padrão
    defaultCurrency: 'BRL',
    
    // Configurações de tema
    theme: {
      primaryColor: '#3B82F6', // blue-500
      secondaryColor: '#6B7280', // gray-500
      successColor: '#10B981', // emerald-500
      dangerColor: '#EF4444', // red-500
      warningColor: '#F59E0B', // amber-500
      infoColor: '#3B82F6', // blue-500
    },
  },
  
  // Configurações de notificação
  notifications: {
    // Tempo de exibição das notificações (em milissegundos)
    duration: 5000,
    
    // Posição das notificações
    position: 'top-right',
  },
};
