'use client';

import { formatCurrency, formatPercentage } from '@/utils/formatters';

export interface CryptoCurrency {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_percentage_24h: number;
  market_cap: number;
  image: string;
}

interface CryptoTableProps {
  cryptos: CryptoCurrency[];
  loading?: boolean;
  error?: string | null;
}

export default function CryptoTable({ cryptos = [], loading = false, error = null }: CryptoTableProps) {

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-600 bg-red-50 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Moeda
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Preço
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              24h %
            </th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Valor de Mercado
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {cryptos.map((crypto) => (
            <tr key={crypto.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <img className="h-8 w-8 rounded-full mr-3" src={crypto.image} alt={crypto.name} />
                  <div>
                    <div className="font-medium text-gray-900">{crypto.name}</div>
                    <div className="text-gray-500 text-sm">{crypto.symbol.toUpperCase()}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                {formatCurrency(crypto.current_price, 'USD')}
              </td>
              <td className={`px-6 py-4 whitespace-nowrap text-right text-sm ${crypto.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatPercentage(crypto.price_change_percentage_24h / 100)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                {formatCurrency(crypto.market_cap, 'USD')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
