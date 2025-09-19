import { NextApiRequest, NextApiResponse } from 'next';

// Verifica se a chave da API está definida
const apiKey = process.env.NEXT_PUBLIC_COINGECKO_API_KEY;

if (!apiKey) {
  console.error('A variável NEXT_PUBLIC_COINGECKO_API_KEY não está definida no arquivo .env');
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  
  try {
    if (!apiKey) {
      throw new Error('Chave da API CoinGecko não configurada');
    }

    const response = await fetch(
      'https://api.coingecko.com/api/v3/global',
      {
        headers: {
          'x-cg-demo-api-key': apiKey as string,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Erro ao buscar estatísticas da CoinGecko');
    }

    const data = await response.json();
    
    res.status(200).json({
      total_criptomoedas: data.data.active_cryptocurrencies,
      volume_24h: data.data.total_volume.usd,
      capitalizacao_mercado: data.data.total_market_cap.usd,
      dominancia_btc: data.data.market_cap_percentage.btc,
      dominancia_eth: data.data.market_cap_percentage.eth,
      atualizado_em: new Date().toISOString()
    });
  } catch (error) {
    console.error('Erro na API de estatísticas:', error);
    res.status(500).json({ error: 'Erro ao buscar estatísticas' });
  }
}
