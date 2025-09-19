-- CreateEnum
CREATE TYPE "crypto_currency" AS ENUM ('BTC', 'ETH', 'ADA', 'SOL', 'XRP', 'DOT', 'AVAX', 'DOGE');

-- CreateTable
CREATE TABLE "crypto_prices" (
    "id" SERIAL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "symbol" "crypto_currency" NOT NULL,
    "price" DECIMAL(20,8) NOT NULL,
    "market_cap" BIGINT,
    "volume_24h" BIGINT,
    "change_24h" DECIMAL(10,4),
    "last_updated" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "crypto_prices_name_key" ON "crypto_prices"("name");

-- CreateIndex
CREATE INDEX "crypto_prices_symbol_idx" ON "crypto_prices"("symbol");

-- CreateIndex
CREATE INDEX "crypto_prices_last_updated_idx" ON "crypto_prices"("last_updated");

-- Enable Row Level Security
ALTER TABLE "crypto_prices" ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access
CREATE POLICY "Enable read access for all users" ON "crypto_prices"
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- Create policy to restrict insert/update/delete to authenticated users
CREATE POLICY "Enable insert for authenticated users only" ON "crypto_prices"
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users only" ON "crypto_prices"
    FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Enable delete for authenticated users only" ON "crypto_prices"
    FOR DELETE
    TO authenticated
    USING (true);
