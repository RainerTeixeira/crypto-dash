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
      `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h`,
      {
        headers: {
          'x-cg-demo-api-key': apiKey as string,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Erro ao buscar dados da CoinGecko');
    }

    const data = await response.json();
    
    // Formata os dados para o formato esperado pelo frontend
    const formattedData = data.map((crypto: any) => ({
      id: crypto.market_cap_rank,
      name: crypto.name,
      symbol: crypto.symbol.toUpperCase(),
      price: crypto.current_price,
      change_24h: crypto.price_change_percentage_24h,
      market_cap: crypto.market_cap,
      volume_24h: crypto.total_volume,
      last_updated: crypto.last_updated
    }));

    res.status(200).json(formattedData);
  } catch (error) {
    console.error('Erro na API de criptomoedas:', error);
    res.status(500).json({ error: 'Erro ao buscar criptomoedas' });
  }
}
