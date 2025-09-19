import { MarketStats as MarketStatsType } from '../types/crypto.types';
import { formatNumber } from '../utils/formatters';
import { FiTrendingUp, FiDollarSign, FiPieChart, FiBarChart2 } from 'react-icons/fi';

interface MarketStatsProps {
  estatisticas: MarketStatsType;
}

const cards = [
  {
    id: 'market-cap',
    title: 'Capitalização de Mercado',
    value: (estatisticas: MarketStatsType) => `$${formatNumber(estatisticas.market_cap)}`,
    icon: <FiTrendingUp className="w-6 h-6 text-blue-600" />,
    change: null,
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-600',
  },
  {
    id: 'volume-24h',
    title: 'Volume 24h',
    value: (estatisticas: MarketStatsType) => `$${formatNumber(estatisticas.volume_24h)}`,
    icon: <FiDollarSign className="w-6 h-6 text-green-600" />,
    change: null,
    bgColor: 'bg-green-50',
    textColor: 'text-green-600',
  },
  {
    id: 'btc-dominance',
    title: 'Dom. Bitcoin',
    value: (estatisticas: MarketStatsType) => `${estatisticas.btc_dominance.toFixed(1)}%`,
    icon: <FiPieChart className="w-6 h-6 text-orange-600" />,
    change: null,
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-600',
  },
  {
    id: 'eth-dominance',
    title: 'Dom. Ethereum',
    value: (estatisticas: MarketStatsType) => `${estatisticas.eth_dominance.toFixed(1)}%`,
    icon: <FiBarChart2 className="w-6 h-6 text-purple-600" />,
    change: null,
    bgColor: 'bg-purple-50',
    textColor: 'text-purple-600',
  },
];

export function MarketStats({ estatisticas }: MarketStatsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card) => (
        <div 
          key={card.id}
          className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-5 border border-gray-100"
        >
          <div className="flex items-center justify-between">
            <div className={`p-2 rounded-lg ${card.bgColor} ${card.textColor}`}>
              {card.icon}
            </div>
            {card.change && (
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                card.change > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {card.change > 0 ? '↑' : '↓'} {Math.abs(card.change)}%
              </span>
            )}
          </div>
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-500">{card.title}</p>
            <p className="text-xl font-semibold text-gray-900 mt-1">
              {card.value(estatisticas)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
