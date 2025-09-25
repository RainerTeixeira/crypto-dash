/**
 * Configuração do Next.js para o Crypto Dashboard
 * 
 * Esta configuração suporta:
 * - Funcionamento em /crypto-dash no domínio rainersoft.com.br
 * - Otimização de imagens da CoinGecko
 * - Configurações de segurança e performance
 */
const isProduction = process.env.NODE_ENV === 'production';

const nextConfig = {
  // Ativa o modo estrito do React para ajudar a identificar problemas
  reactStrictMode: true,
  
  // Configuração de imagens
  images: {
    // Domínios permitidos para otimização de imagens
    domains: ['assets.coingecko.com'],
    // Desativa otimização de imagens em desenvolvimento para melhor performance
    unoptimized: !isProduction,
  },
  
  // Configuração de redirecionamento
  async rewrites() {
    return [
      {
        source: '/crypto-dash',
        destination: '/crypto-dash',
      },
      {
        source: '/crypto-dash/:path*',
        destination: '/crypto-dash/:path*',
      },
    ];
  },

  // Cabeçalhos de segurança e cache
  async headers() {
    return [
      // Cabeçalhos de segurança padrão para todas as rotas da aplicação.
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
      // Cabeçalhos de cache para a API
      {
        source: '/api/criptomoedas',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, s-maxage=60, stale-while-revalidate=300',
          },
        ],
      },
      {
        source: '/api/estatisticas',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, s-maxage=300, stale-while-revalidate=600',
          },
        ],
      },
    ];
  },

  // Configuração de variáveis de ambiente públicas
  env: {
    // Adicione aqui variáveis de ambiente que devem estar disponíveis no navegador
    // Exemplo: API_URL: process.env.API_URL,
  },
};

module.exports = nextConfig;
