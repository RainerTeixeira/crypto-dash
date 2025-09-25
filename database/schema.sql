-- =============================================
-- 📊 Crypto Dashboard - Database Schema (Public Access)
-- =============================================
-- Schema otimizado para acesso público direto
-- Sem autenticação JWT - dados abertos
-- =============================================

-- 1. Criar tipos ENUM
CREATE TYPE public.crypto_currency AS ENUM (
    'BTC', 'ETH', 'ADA', 'SOL', 'XRP', 'DOT', 'AVAX', 'DOGE',
    'BNB', 'MATIC', 'LTC', 'LINK', 'UNI', 'ATOM', 'XLM', 'ETC',
    'BCH', 'ALGO', 'MANA', 'SAND', 'AXS', 'GRT', 'FTT', 'RUNE'
);

-- 2. Tabela de criptomoedas principais
CREATE TABLE public.cryptocurrencies (
    id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    image_url TEXT,
    description TEXT,
    website_url TEXT,
    github_url TEXT,
    market_cap_rank INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para cryptocurrencies
CREATE INDEX idx_cryptocurrencies_symbol ON public.cryptocurrencies(symbol);
CREATE INDEX idx_cryptocurrencies_market_cap_rank ON public.cryptocurrencies(market_cap_rank);

-- 3. Tabela de histórico de preços (dados públicos)
CREATE TABLE public.crypto_prices (
    id BIGSERIAL PRIMARY KEY,
    cryptocurrency_id VARCHAR(50) NOT NULL REFERENCES public.cryptocurrencies(id) ON DELETE CASCADE,
    symbol public.crypto_currency NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    market_cap DECIMAL(30,2),
    volume_24h DECIMAL(30,2),
    change_24h DECIMAL(10,4),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL,
    -- Dados adicionais da API CoinGecko
    high_24h DECIMAL(20,8),
    low_24h DECIMAL(20,8),
    price_change_24h DECIMAL(20,8),
    market_cap_change_24h DECIMAL(30,2),
    market_cap_change_percentage_24h DECIMAL(10,4),
    circulating_supply DECIMAL(30,8),
    total_supply DECIMAL(30,8),
    max_supply DECIMAL(30,8),
    ath DECIMAL(20,8),
    ath_change_percentage DECIMAL(10,4),
    ath_date TIMESTAMP WITH TIME ZONE,
    atl DECIMAL(20,8),
    atl_change_percentage DECIMAL(10,4),
    atl_date TIMESTAMP WITH TIME ZONE,
    roi JSONB,
    last_updated_from_api TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices otimizados para crypto_prices
CREATE INDEX idx_crypto_prices_cryptocurrency_id ON public.crypto_prices(cryptocurrency_id);
CREATE INDEX idx_crypto_prices_symbol ON public.crypto_prices(symbol);
CREATE INDEX idx_crypto_prices_last_updated ON public.crypto_prices(last_updated);
CREATE INDEX idx_crypto_prices_symbol_last_updated ON public.crypto_prices(symbol, last_updated DESC);
CREATE INDEX idx_crypto_prices_price ON public.crypto_prices(price);
CREATE INDEX idx_crypto_prices_market_cap ON public.crypto_prices(market_cap);

-- 4. Tabela de estatísticas globais de mercado
CREATE TABLE public.market_stats (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    active_cryptocurrencies INTEGER,
    total_market_cap_usd DECIMAL(40,2),
    total_volume_usd_24h DECIMAL(40,2),
    market_cap_percentage JSONB,
    market_cap_change_percentage_24h_usd DECIMAL(10,4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para market_stats
CREATE INDEX idx_market_stats_timestamp ON public.market_stats(timestamp);

-- 5. Tabela de últimos preços (cache otimizado)
CREATE TABLE public.latest_prices (
    cryptocurrency_id VARCHAR(50) PRIMARY KEY REFERENCES public.cryptocurrencies(id) ON DELETE CASCADE,
    symbol public.crypto_currency NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    market_cap DECIMAL(30,2),
    volume_24h DECIMAL(30,2),
    change_24h DECIMAL(10,4),
    high_24h DECIMAL(20,8),
    low_24h DECIMAL(20,8),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL,
    last_crypto_price_id BIGINT NOT NULL REFERENCES public.crypto_prices(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para latest_prices
CREATE INDEX idx_latest_prices_symbol ON public.latest_prices(symbol);
CREATE INDEX idx_latest_prices_last_updated ON public.latest_prices(last_updated);
CREATE INDEX idx_latest_prices_price ON public.latest_prices(price);

-- =============================================
-- 6. Row Level Security (RLS) - Configurado para ACESSO PÚBLICO
-- =============================================

-- Habilita RLS em todas as tabelas
ALTER TABLE public.cryptocurrencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.crypto_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.latest_prices ENABLE ROW LEVEL SECURITY;

-- Políticas RLS - PERMITE LEITURA PÚBLICA TOTAL
CREATE POLICY "Allow full public access to cryptocurrencies" ON public.cryptocurrencies
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow full public access to crypto_prices" ON public.crypto_prices
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow full public access to market_stats" ON public.market_stats
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow full public access to latest_prices" ON public.latest_prices
    FOR ALL USING (true) WITH CHECK (true);

-- =============================================
-- 7. Funções de Utilidade
-- =============================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_cryptocurrencies_updated_at BEFORE UPDATE ON public.cryptocurrencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_latest_prices_updated_at BEFORE UPDATE ON public.latest_prices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 8. Views para Consultas Otimizadas
-- =============================================

-- View para estatísticas consolidadas (ACESSO PÚBLICO)
CREATE OR REPLACE VIEW public.crypto_market_overview AS
SELECT
    c.id,
    c.symbol,
    c.name,
    c.market_cap_rank,
    lp.price,
    lp.market_cap,
    lp.volume_24h,
    lp.change_24h,
    lp.high_24h,
    lp.low_24h,
    lp.last_updated,
    ms.total_market_cap_usd as global_market_cap,
    ms.total_volume_usd_24h as global_volume_24h
FROM public.cryptocurrencies c
JOIN public.latest_prices lp ON c.id = lp.cryptocurrency_id
LEFT JOIN public.market_stats ms ON ms.timestamp >= lp.last_updated - INTERVAL '1 hour'
ORDER BY c.market_cap_rank;

-- View para top 10 criptomoedas por market cap
CREATE OR REPLACE VIEW public.top_10_cryptos AS
SELECT * FROM public.crypto_market_overview
WHERE market_cap_rank <= 10;

-- =============================================
-- 9. Funções RPC (Remote Procedure Calls)
-- =============================================

-- Função para obter versão do PostgreSQL (usada para health check)
CREATE OR REPLACE FUNCTION public.version()
RETURNS TABLE(version text) AS $$
BEGIN
    RETURN QUERY SELECT version();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para obter estatísticas de mercado agregadas
CREATE OR REPLACE FUNCTION public.get_market_stats()
RETURNS TABLE(
    volume_24h DECIMAL,
    market_cap DECIMAL,
    btc_dominance DECIMAL,
    eth_dominance DECIMAL,
    active_cryptocurrencies INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(lp.volume_24h), 0) as volume_24h,
        COALESCE(SUM(lp.market_cap), 0) as market_cap,
        CASE 
            WHEN SUM(lp.market_cap) > 0 THEN 
                (SELECT (market_cap / SUM(lp.market_cap) * 100) 
                 FROM public.latest_prices 
                 WHERE symbol = 'BTC' 
                 LIMIT 1)
            ELSE 0 
        END as btc_dominance,
        CASE 
            WHEN SUM(lp.market_cap) > 0 THEN 
                (SELECT (market_cap / SUM(lp.market_cap) * 100) 
                 FROM public.latest_prices 
                 WHERE symbol = 'ETH' 
                 LIMIT 1)
            ELSE 0 
        END as eth_dominance,
        COUNT(*)::INTEGER as active_cryptocurrencies
    FROM public.latest_prices lp
    WHERE lp.market_cap > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para obter dados históricos de uma criptomoeda
CREATE OR REPLACE FUNCTION public.get_crypto_history(
    crypto_id_param VARCHAR(50),
    days_param INTEGER DEFAULT 30
)
RETURNS TABLE(
    data DATE,
    preco DECIMAL(20,8),
    volume DECIMAL(30,2),
    market_cap DECIMAL(30,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(cp.last_updated) as data,
        cp.price as preco,
        cp.volume_24h as volume,
        cp.market_cap as market_cap
    FROM public.crypto_prices cp
    WHERE cp.cryptocurrency_id = crypto_id_param
        AND cp.last_updated >= NOW() - INTERVAL '1 day' * days_param
    ORDER BY cp.last_updated DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para obter top gainers (maiores ganhadores)
CREATE OR REPLACE FUNCTION public.get_top_gainers(limit_param INTEGER DEFAULT 5)
RETURNS TABLE(
    cryptocurrency_id VARCHAR(50),
    symbol VARCHAR(10),
    name VARCHAR(100),
    price DECIMAL(20,8),
    change_24h DECIMAL(10,4),
    market_cap DECIMAL(30,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lp.cryptocurrency_id,
        lp.symbol::VARCHAR(10),
        c.name,
        lp.price,
        lp.change_24h,
        lp.market_cap
    FROM public.latest_prices lp
    JOIN public.cryptocurrencies c ON lp.cryptocurrency_id = c.id
    WHERE lp.change_24h IS NOT NULL
    ORDER BY lp.change_24h DESC
    LIMIT limit_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para obter top losers (maiores perdedores)
CREATE OR REPLACE FUNCTION public.get_top_losers(limit_param INTEGER DEFAULT 5)
RETURNS TABLE(
    cryptocurrency_id VARCHAR(50),
    symbol VARCHAR(10),
    name VARCHAR(100),
    price DECIMAL(20,8),
    change_24h DECIMAL(10,4),
    market_cap DECIMAL(30,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lp.cryptocurrency_id,
        lp.symbol::VARCHAR(10),
        c.name,
        lp.price,
        lp.change_24h,
        lp.market_cap
    FROM public.latest_prices lp
    JOIN public.cryptocurrencies c ON lp.cryptocurrency_id = c.id
    WHERE lp.change_24h IS NOT NULL
    ORDER BY lp.change_24h ASC
    LIMIT limit_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para atualizar latest_prices automaticamente
CREATE OR REPLACE FUNCTION public.update_latest_prices()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
BEGIN
    -- Atualiza latest_prices com os dados mais recentes de crypto_prices
    WITH latest_data AS (
        SELECT DISTINCT ON (cryptocurrency_id)
            cryptocurrency_id,
            symbol,
            price,
            market_cap,
            volume_24h,
            change_24h,
            high_24h,
            low_24h,
            last_updated,
            id as last_crypto_price_id
        FROM public.crypto_prices
        ORDER BY cryptocurrency_id, last_updated DESC
    )
    INSERT INTO public.latest_prices (
        cryptocurrency_id, symbol, price, market_cap, volume_24h, 
        change_24h, high_24h, low_24h, last_updated, last_crypto_price_id
    )
    SELECT 
        ld.cryptocurrency_id,
        ld.symbol,
        ld.price,
        ld.market_cap,
        ld.volume_24h,
        ld.change_24h,
        ld.high_24h,
        ld.low_24h,
        ld.last_updated,
        ld.last_crypto_price_id
    FROM latest_data ld
    ON CONFLICT (cryptocurrency_id) 
    DO UPDATE SET
        symbol = EXCLUDED.symbol,
        price = EXCLUDED.price,
        market_cap = EXCLUDED.market_cap,
        volume_24h = EXCLUDED.volume_24h,
        change_24h = EXCLUDED.change_24h,
        high_24h = EXCLUDED.high_24h,
        low_24h = EXCLUDED.low_24h,
        last_updated = EXCLUDED.last_updated,
        last_crypto_price_id = EXCLUDED.last_crypto_price_id,
        updated_at = NOW();

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- 10. Triggers para Manutenção Automática
-- =============================================

-- Trigger para atualizar latest_prices quando crypto_prices é atualizada
CREATE OR REPLACE FUNCTION public.trigger_update_latest_prices()
RETURNS TRIGGER AS $$
BEGIN
    -- Chama a função de atualização
    PERFORM public.update_latest_prices();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger que executa após INSERT/UPDATE na tabela crypto_prices
CREATE TRIGGER trigger_crypto_prices_update_latest
    AFTER INSERT OR UPDATE ON public.crypto_prices
    FOR EACH STATEMENT
    EXECUTE FUNCTION public.trigger_update_latest_prices();

-- =============================================
-- 📝 COMENTÁRIOS FINAIS
-- =============================================
--
-- Este schema foi projetado para:
-- ✅ Acesso público total - sem autenticação
-- ✅ Consultas otimizadas e rápidas
-- ✅ Manter histórico completo de preços
-- ✅ Performance otimizada com índices
-- ✅ Ser escalável e performático
-- ✅ Suporte completo ao processo ETL
-- ✅ Funções RPC para operações complexas
-- ✅ Manutenção automática de dados
--
-- Para uso público:
-- 1. Todas as tabelas permitem SELECT, INSERT, UPDATE, DELETE
-- 2. Não há restrições de RLS para leitura
-- 3. Views otimizadas para consultas comuns
-- 4. Índices estratégicos para performance
-- 5. Funções RPC para operações agregadas
-- 6. Triggers para manutenção automática
-- =============================================
