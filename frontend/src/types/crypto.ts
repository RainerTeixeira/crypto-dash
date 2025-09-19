/**
 * Interface que define a estrutura de dados de uma criptomoeda
 */
export interface Criptomoeda {
  id: number;              // Identificador único
  name: string;            // Nome da criptomoeda (ex: "Bitcoin")
  symbol: string;          // Símbolo (ex: "btc")
  price: number;           // Preço atual em USD
  change_24h: number;      // Variação percentual nas últimas 24h
  market_cap: number;      // Capitalização de mercado
  volume_24h: number;      // Volume de negociação nas últimas 24h
  last_updated: string;    // Data/hora da última atualização
  image?: string;          // URL da imagem da criptomoeda (opcional)
}

/**
 * Interface que define a estrutura das estatísticas do mercado
 */
export interface EstatisticasMercado {
  total_criptomoedas: number;    // Número total de criptomoedas
  volume_24h: number;           // Volume total de negociação nas últimas 24h
  capitalizacao_mercado: number; // Capitalização total de mercado
  dominancia_btc: number;        // Porcentagem de dominância do Bitcoin
  dominancia_eth: number;        // Porcentagem de dominância do Ethereum
  atualizado_em: string;         // Data/hora da última atualização
}

/**
 * Interface para os dados do gráfico de preços
 */
export interface DadosGrafico {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }[];
}
