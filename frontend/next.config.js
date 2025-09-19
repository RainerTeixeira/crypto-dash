/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production';
const basePath = '/crypto-dash';

const nextConfig = {
  reactStrictMode: true,
  // Configura o basePath para /crypto-dash
  basePath: isProd ? basePath : '',
  // Configura o assetPrefix para produção
  assetPrefix: isProd ? `https://rainersoft.com.br${basePath}` : '',
  images: {
    domains: ['assets.coingecko.com'],
    // Configura o path para imagens funcionarem com o basePath
    path: isProd ? `${basePath}/_next/image` : '/_next/image',
  },
  // Configuração para expor as variáveis de ambiente no lado do cliente
  env: {
    // Garante que as rotas da API usem o basePath correto
    NEXT_PUBLIC_BASE_PATH: isProd ? basePath : '',
    NEXT_PUBLIC_API_BASE_URL: isProd 
      ? 'https://api.rainersoft.com.br/api'
      : 'http://localhost:8000/api',
  },
  // Configuração de headers para a API da CoinGecko
  async headers() {
    return [
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
  // Configuração de rewrites para a API
  async rewrites() {
    return [
      // Em produção, redireciona /api/* para a API correta
      {
        source: '/api/:path*',
        destination: isProd 
          ? 'https://api.rainersoft.com.br/api/:path*'
          : 'http://localhost:8000/api/:path*',
      },
      // Mantém as configurações existentes para desenvolvimento
      ...(isProd ? [] : [
        {
          source: '/api/backend/:path*',
          destination: process.env.NEXT_PUBLIC_API_BASE_URL
            ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/:path*`
            : 'http://localhost:8000/api/:path*',
        },
      ]),
    ];
  },
};

module.exports = nextConfig;
