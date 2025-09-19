/**
 * Interface defining the structure of cryptocurrency data
 */
export interface Cryptocurrency {
  id: number;              // Unique identifier
  name: string;            // Cryptocurrency name (e.g., "Bitcoin")
  symbol: string;          // Symbol (e.g., "btc")
  price: number;           // Current price in USD
  change_24h: number;      // 24-hour price change percentage
  market_cap: number;      // Market capitalization
  volume_24h: number;      // 24-hour trading volume
  last_updated: string;    // Last update timestamp
  image?: string;          // URL of the cryptocurrency image (optional)
}

/**
 * Interface defining the structure of market statistics
 */
export interface MarketStats {
  total_cryptocurrencies: number;  // Total number of cryptocurrencies
  volume_24h: number;             // 24-hour trading volume
  market_cap: number;             // Total market capitalization
  btc_dominance: number;          // Bitcoin dominance percentage
  eth_dominance: number;          // Ethereum dominance percentage
  updated_at: string;             // Last update timestamp
}

/**
 * Interface for price chart data
 */
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    tension: number;
  }[];
}
