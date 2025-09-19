-- 1. Criar o tipo ENUM para as criptomoedas
CREATE TYPE public.crypto_currency AS ENUM (
    'BTC', 'ETH', 'ADA', 'SOL', 'XRP', 'DOT', 'AVAX', 'DOGE',
    'BNB', 'MATIC', 'LTC', 'LINK', 'UNI', 'ATOM', 'XLM', 'ETC'
);

-- 2. Tabela de histórico de preços
CREATE TABLE public.crypto_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol public.crypto_currency NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    price_change DECIMAL(20,8),
    price_change_percent DECIMAL(10,4),
    weighted_avg_price DECIMAL(20,8),
    prev_close_price DECIMAL(20,8),
    last_qty DECIMAL(20,8),
    bid_price DECIMAL(20,8),
    ask_price DECIMAL(20,8),
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) NOT NULL,
    quote_volume DECIMAL(30,8) NOT NULL,
    open_time TIMESTAMP WITH TIME ZONE NOT NULL,
    close_time TIMESTAMP WITH TIME ZONE NOT NULL,
    first_id BIGINT,
    last_id BIGINT,
    count BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Índices para crypto_prices
CREATE INDEX idx_crypto_prices_symbol ON public.crypto_prices(symbol);
CREATE INDEX idx_crypto_prices_close_time ON public.crypto_prices(close_time);
CREATE INDEX idx_crypto_prices_symbol_close_time ON public.crypto_prices(symbol, close_time DESC);

-- 3. Tabela de últimos preços
CREATE TABLE public.latest_prices (
    symbol public.crypto_currency PRIMARY KEY,
    price DECIMAL(20,8) NOT NULL,
    price_change DECIMAL(20,8),
    price_change_percent DECIMAL(10,4),
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) NOT NULL,
    quote_volume DECIMAL(30,8) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL,
    last_crypto_price_id BIGINT NOT NULL
);

-- Índices para latest_prices
CREATE INDEX idx_latest_prices_last_updated ON public.latest_prices(last_updated);
