/**
 * Página principal do Dashboard de Criptomoedas
 * 
 * Este componente exibe uma visão geral do mercado de criptomoedas, incluindo:
 * - Estatísticas gerais do mercado
 * - Lista de criptomoedas com preços, variação e volume
 * - Atualização automática a cada minuto
 */

// Importações de bibliotecas e componentes
import { useEffect, useState } from 'react';  // Hooks do React
import Head from 'next/head';  // Componente para gerenciar o cabeçalho da página
import { FiArrowUp, FiArrowDown, FiRefreshCw } from 'react-icons/fi';  // Ícones da Feather Icons

// Import types from crypto.types.ts
import { Cryptocurrency, MarketStats } from '../src/types/crypto.types';

/**
 * Componente principal da página inicial
 */
export default function Home() {
  // Component states
  const [cryptos, setCryptos] = useState<Cryptocurrency[]>([]);    // List of cryptocurrencies
  const [marketStats, setMarketStats] = useState<MarketStats | null>(null);  // Market statistics
  const [carregando, setCarregando] = useState(true);              // Estado de carregamento
  const [erro, setErro] = useState<string | null>(null);           // Mensagem de erro, se houver
  const [atualizando, setAtualizando] = useState(false);           // Estado de atualização manual

  /**
   * Função assíncrona para buscar dados da API
   * Atualiza tanto a lista de criptomoedas quanto as estatísticas do mercado
   */
  const buscarDados = async () => {
    try {
      setAtualizando(true);
      setErro(null);
      
      // Make parallel requests to improve performance
      const [resCripto, resEstatisticas] = await Promise.all([
        fetch('/api/cryptocurrencies'),
        fetch('/api/market-stats')
      ]);
      
      // Verifica se as requisições foram bem-sucedidas
      if (!resCripto.ok || !resEstatisticas.ok) {
        throw new Error('Erro ao buscar dados da API');
      }
      
      // Converte as respostas para JSON
      const dadosCripto = await resCripto.json();
      const dadosEstatisticas = await resEstatisticas.json();
      
      // Update states with the received data
      setCryptos(dadosCripto);
      setMarketStats(dadosEstatisticas);
    } catch (err) {
      // Em caso de erro, armazena a mensagem de erro
      setErro(err instanceof Error ? err.message : 'Ocorreu um erro inesperado');
    } finally {
      // Independente do resultado, finaliza os estados de carregamento
      setCarregando(false);
    }
  };

  // Efeito colateral que executa ao montar o componente
  useEffect(() => {
    // Fetch initial data
    buscarDados();
  
    // Set up an interval to update data every minute
    const intervalo = setInterval(buscarDados, 60000);
  
    // Cleanup function that runs when the component unmounts
    return () => clearInterval(intervalo);
  }, []); // Array de dependências vazio = executa apenas uma vez ao montar

  /**
   * Formata um valor numérico como moeda (USD)
   */
  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8  // Permite até 8 casas decimais para criptomoedas de baixo valor
    }).format(valor);
  };

  /**
   * Formata um número grande em formato compacto (ex: 1.5M, 2.3B)
   */
  const formatarNumero = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      notation: 'compact',
      compactDisplay: 'short',
      maximumFractionDigits: 1
    }).format(valor);
  };

  // Check if data is loading
  if (carregando) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  // If there's an error, show the error message
  if (erro) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error loading data</h1>
          <p className="text-gray-600 mb-6">{erro}</p>
          <button
            onClick={buscarDados}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  // Main render
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page header */}
      <Head>
        <title>Crypto Dashboard</title>
        <meta name="description" content="Track real-time cryptocurrency prices and market data" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Navigation bar */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Crypto Dashboard</h1>
          <button
            onClick={buscarDados}
            disabled={atualizando}
            className={`flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors`}
            aria-label="Refresh data"
          >
            <FiRefreshCw className={`mr-2 ${atualizando ? 'animate-spin' : ''}`} />
            {atualizando ? 'Updating...' : 'Refresh'}
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Crypto Dashboard</h1>
          <button
            onClick={buscarDados}
            disabled={atualizando}
            className={`flex items-center px-4 py-2 rounded-md ${atualizando ? 'bg-gray-300' : 'bg-blue-600 hover:bg-blue-700'} text-white`}
          >
            {atualizando ? (
              <>
                <FiRefreshCw className="animate-spin mr-2" />
                Updating...
              </>
            ) : (
              <>
                <FiRefreshCw className="mr-2" />
                Refresh
              </>
            )}
          </button>
        </div>

        {/* Display error message if any */}
        {erro && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
            <p className="font-bold">Error</p>
            <p>{erro}</p>
          </div>
        )}

        {/* Market Stats Section */}
        {marketStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">Total Cryptocurrencies</p>
              <p className="text-2xl font-bold">{marketStats.total_cryptocurrencies.toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">24h Volume</p>
              <p className="text-2xl font-bold">${(marketStats.volume_24h / 1e9).toFixed(2)}B</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">Market Cap</p>
              <p className="text-2xl font-bold">${(marketStats.market_cap / 1e12).toFixed(2)}T</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <p className="text-sm text-gray-500">BTC/ETH Dominance</p>
              <p className="text-2xl font-bold">
                {marketStats.btc_dominance.toFixed(1)}% / {marketStats.eth_dominance.toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {/* Cryptocurrencies Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    24h %
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    24h Volume
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Cap
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cryptos.map((crypto) => (
                  <tr key={crypto.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 font-bold">
                          {crypto.symbol.substring(0, 3).toUpperCase()}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{crypto.name}</div>
                          <div className="text-sm text-gray-500">{crypto.symbol.toUpperCase()}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                      ${crypto.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-right text-sm ${crypto.change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      <div className="flex items-center justify-end">
                        {crypto.change_24h >= 0 ? (
                          <FiArrowUp className="mr-1" />
                        ) : (
                          <FiArrowDown className="mr-1" />
                        )}
                        {Math.abs(crypto.change_24h).toFixed(2)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      ${(crypto.volume_24h / 1e6).toFixed(2)}M
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      ${(crypto.market_cap / 1e9).toFixed(2)}B
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          <p>Real-time data. Auto-updates every minute.</p>
        </div>
      </footer>
    </div>
  );
}
