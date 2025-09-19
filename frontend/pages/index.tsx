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

// Definição dos tipos TypeScript para tipagem estática

/**
 * Interface que define a estrutura de dados de uma criptomoeda
 */
type Criptomoeda = {
  id: number;              // Identificador único
  name: string;            // Nome da criptomoeda (ex: "Bitcoin")
  symbol: string;          // Símbolo (ex: "btc")
  price: number;           // Preço atual em USD
  change_24h: number;      // Variação percentual nas últimas 24h
  market_cap: number;      // Capitalização de mercado
  volume_24h: number;      // Volume de negociação nas últimas 24h
  last_updated: string;    // Data/hora da última atualização
};

/**
 * Interface que define a estrutura das estatísticas do mercado
 */
type Estatisticas = {
  total_criptomoedas: number;    // Número total de criptomoedas
  volume_24h: number;           // Volume total de negociação nas últimas 24h
  capitalizacao_mercado: number; // Capitalização total de mercado
  dominancia_btc: number;        // Porcentagem de dominância do Bitcoin
  dominancia_eth: number;        // Porcentagem de dominância do Ethereum
  atualizado_em: string;         // Data/hora da última atualização
};

/**
 * Componente principal da página inicial
 */
export default function Home() {
  // Estados do componente
  const [dados, setDados] = useState<Criptomoeda[]>([]);           // Lista de criptomoedas
  const [estatisticas, setEstatisticas] = useState<Estatisticas | null>(null);  // Estatísticas do mercado
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
      
      // Faz requisições paralelas para melhorar o desempenho
      const [resCripto, resEstatisticas] = await Promise.all([
        fetch('/api/criptomoedas'),
        fetch('/api/estatisticas')
      ]);
      
      // Verifica se as requisições foram bem-sucedidas
      if (!resCripto.ok || !resEstatisticas.ok) {
        throw new Error('Erro ao buscar dados da API');
      }
      
      // Converte as respostas para JSON
      const dadosCripto = await resCripto.json();
      const dadosEstatisticas = await resEstatisticas.json();
      
      // Atualiza os estados com os dados recebidos
      setDados(dadosCripto);
      setEstatisticas(dadosEstatisticas);
    } catch (err) {
      // Em caso de erro, armazena a mensagem de erro
      setErro(err instanceof Error ? err.message : 'Ocorreu um erro inesperado');
    } finally {
      // Independente do resultado, finaliza os estados de carregamento
      setCarregando(false);
      setAtualizando(false);
    }
  };

  // Efeito colateral que executa ao montar o componente
  useEffect(() => {
    // Busca os dados iniciais
    buscarDados();
    
    // Configura um intervalo para atualizar os dados a cada minuto
    const intervalo = setInterval(buscarDados, 60000);
    
    // Função de limpeza que é executada quando o componente é desmontado
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

  // Estado de carregamento
  if (carregando) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          {/* Ícone de carregamento animado */}
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados de criptomoedas...</p>
        </div>
      </div>
    );
  }

  // Estado de erro
  if (erro) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 px-4">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erro ao carregar os dados</h2>
          <p className="text-gray-600 mb-6">{erro}</p>
          <button
            onClick={buscarDados}
            disabled={atualizando}
            className={`px-4 py-2 rounded-md text-white ${atualizando ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'} transition-colors`}
          >
            {atualizando ? 'Atualizando...' : 'Tentar novamente'}
          </button>
        </div>
      </div>
    );
  }

  // Renderização principal
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Cabeçalho da página */}
      <Head>
        <title>Dashboard de Criptomoedas</title>
        <meta name="description" content="Acompanhe as cotações das principais criptomoedas em tempo real" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Barra de navegação */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">CryptoDash</h1>
          <button
            onClick={buscarDados}
            disabled={atualizando}
            className="flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors"
            aria-label="Atualizar dados"
          >
            <FiRefreshCw className={`mr-2 ${atualizando ? 'animate-spin' : ''}`} />
            {atualizando ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>
      </header>

      {/* Conteúdo principal */}
      <main className="container mx-auto px-4 py-8">
        {/* Seção de Estatísticas */}
        {estatisticas && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {/* Cartão de Capitalização de Mercado */}
            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
              <p className="text-sm text-gray-500">Capitalização de Mercado</p>
              <p className="text-xl font-semibold">${formatarNumero(estatisticas.capitalizacao_mercado)}</p>
            </div>
            
            {/* Cartão de Volume 24h */}
            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
              <p className="text-sm text-gray-500">Volume 24h</p>
              <p className="text-xl font-semibold">${formatarNumero(estatisticas.volume_24h)}</p>
            </div>
            
            {/* Cartão de Dominância do Bitcoin */}
            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
              <p className="text-sm text-gray-500">Dom. BTC</p>
              <p className="text-xl font-semibold">{estatisticas.dominancia_btc.toFixed(1)}%</p>
            </div>
            
            {/* Cartão de Dominância do Ethereum */}
            <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
              <p className="text-sm text-gray-500">Dom. ETH</p>
              <p className="text-xl font-semibold">{estatisticas.dominancia_eth.toFixed(1)}%</p>
            </div>
          </div>
        )}

        {/* Tabela de Criptomoedas */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Criptomoeda</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Preço (USD)</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Variação 24h</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Volume 24h</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Valor de Mercado</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dados.map((cripto) => (
                  <tr key={cripto.id} className="hover:bg-gray-50 transition-colors">
                    {/* Coluna do nome e símbolo */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 font-bold">
                          {cripto.symbol.substring(0, 3).toUpperCase()}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{cripto.name}</div>
                          <div className="text-sm text-gray-500">{cripto.symbol.toUpperCase()}</div>
                        </div>
                      </div>
                    </td>
                    
                    {/* Coluna do preço */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                      {formatarMoeda(cripto.price)}
                    </td>
                    
                    {/* Coluna da variação 24h */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <span className={`inline-flex items-center ${cripto.change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {cripto.change_24h >= 0 ? (
                          <FiArrowUp className="mr-1" />
                        ) : (
                          <FiArrowDown className="mr-1" />
                        )}
                        {Math.abs(cripto.change_24h).toFixed(2)}%
                      </span>
                    </td>
                    
                    {/* Coluna do volume 24h */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      ${formatarNumero(cripto.volume_24h)}
                    </td>
                    
                    {/* Coluna da capitalização de mercado */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      ${formatarNumero(cripto.market_cap)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Rodapé */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-500">
            Dados atualizados em {new Date().toLocaleString('pt-BR')}
          </p>
          <p className="text-center text-xs text-gray-400 mt-2">
            Os dados são fornecidos pela CoinGecko API e atualizados a cada minuto.
          </p>
        </div>
      </footer>
    </div>
  );
}
