import { Cryptocurrency } from '../types/crypto.types';
import { formatCurrency, formatNumber, formatPercentage } from '../utils/formatters';
import { FiArrowUp, FiArrowDown } from 'react-icons/fi';

interface CryptoCardProps {
  crypto: Cryptocurrency;
  onClick?: () => void;
}

export function CryptoCard({ crypto, onClick }: CryptoCardProps) {
  const isPositive = crypto.change_24h >= 0;
  
  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-4 cursor-pointer border border-gray-100"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold">
            {crypto.symbol.substring(0, 3).toUpperCase()}
          </div>
          <div className="ml-3">
            <h3 className="font-semibold text-gray-900">{crypto.name}</h3>
            <span className="text-xs text-gray-500">{crypto.symbol.toUpperCase()}</span>
          </div>
        </div>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          isPositive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isPositive ? (
            <FiArrowUp className="mr-1" />
          ) : (
            <FiArrowDown className="mr-1" />
          )}
          {formatPercentage(crypto.change_24h)}
        </span>
      </div>
      
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-500 mb-1">
          <span>Preço</span>
          <span className="text-gray-900 font-medium">{formatCurrency(crypto.price)}</span>
        </div>
        <div className="flex justify-between text-sm text-gray-500">
          <span>Volume 24h</span>
          <span>${formatNumber(crypto.volume_24h)}</span>
        </div>
      </div>
    </div>
  );
}
