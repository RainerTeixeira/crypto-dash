'use client';

import { useState, useEffect } from 'react';
import CryptoTable, { CryptoCurrency } from '@/components/crypto/CryptoTable';
import { APP_CONFIG } from '@/utils/config';

export default function Cryptocurrencies() {
  const [cryptos, setCryptos] = useState<CryptoCurrency[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCryptos = async () => {
      try {
        const response = await fetch(`${APP_CONFIG.api.baseUrl}${APP_CONFIG.api.endpoints.cryptocurrencies}`);
        if (!response.ok) {
          throw new Error('Erro ao buscar criptomoedas');
        }
        const data = await response.json();
        setCryptos(data);
      } catch (err) {
        setError('Erro ao carregar criptomoedas. Tente novamente mais tarde.');
        console.error('Erro ao buscar criptomoedas:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCryptos();
    
    // Atualizar a cada 60 segundos
    const interval = setInterval(fetchCryptos, 60000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Cotações de Criptomoedas
      </h1>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <CryptoTable 
          cryptos={cryptos}
          loading={loading}
          error={error}
        />
      </div>
    </div>
  );
}
