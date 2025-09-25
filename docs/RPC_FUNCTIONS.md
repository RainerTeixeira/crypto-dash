# 🗄️ Documentação das Funções RPC

Este documento descreve as funções RPC (Remote Procedure Calls) implementadas no banco de dados PostgreSQL do projeto Crypto Dashboard.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funções Implementadas](#funções-implementadas)
- [Exemplos de Uso](#exemplos-de-uso)
- [Tratamento de Erros](#tratamento-de-erros)

## 🔍 Visão Geral

As funções RPC são stored procedures PostgreSQL que executam operações complexas diretamente no banco de dados, oferecendo:

- **Performance Otimizada**: Operações agregadas executadas no servidor de banco
- **Reutilização**: Lógica de negócio centralizada e reutilizável
- **Segurança**: Execução com privilégios controlados (`SECURITY DEFINER`)
- **Manutenibilidade**: Código SQL centralizado e versionado

## 🛠️ Funções Implementadas

### 1. `version()`

**Propósito**: Health check do banco de dados PostgreSQL

**Retorno**:

```sql
TABLE(version text)
```

**Exemplo de Uso**:

```sql
SELECT * FROM public.version();
```

**Resposta**:

```
version
PostgreSQL 15.4 on x86_64-pc-linux-gnu...
```

---

### 2. `get_market_stats()`

**Propósito**: Obtém estatísticas agregadas do mercado de criptomoedas

**Retorno**:

```sql
TABLE(
    volume_24h DECIMAL,
    market_cap DECIMAL,
    btc_dominance DECIMAL,
    eth_dominance DECIMAL,
    active_cryptocurrencies INTEGER
)
```

**Exemplo de Uso**:

```sql
SELECT * FROM public.get_market_stats();
```

**Resposta**:

```
volume_24h        | market_cap         | btc_dominance | eth_dominance | active_cryptocurrencies
123456789012      | 2345678901234      | 42.5          | 18.7          | 1250
```

---

### 3. `get_crypto_history(crypto_id_param, days_param)`

**Propósito**: Obtém dados históricos de uma criptomoeda específica

**Parâmetros**:

- `crypto_id_param VARCHAR(50)` - ID da criptomoeda
- `days_param INTEGER DEFAULT 30` - Número de dias de histórico

**Retorno**:

```sql
TABLE(
    data DATE,
    preco DECIMAL(20,8),
    volume DECIMAL(30,2),
    market_cap DECIMAL(30,2)
)
```

**Exemplo de Uso**:

```sql
SELECT * FROM public.get_crypto_history('bitcoin', 7);
```

**Resposta**:

```
data       | preco     | volume         | market_cap
2024-01-01 | 45000.00  | 25000000000   | 850000000000
2024-01-02 | 45500.00  | 26000000000   | 860000000000
...
```

---

### 4. `get_top_gainers(limit_param)`

**Propósito**: Obtém as criptomoedas com maior ganho nas últimas 24h

**Parâmetros**:

- `limit_param INTEGER DEFAULT 5` - Número de resultados

**Retorno**:

```sql
TABLE(
    cryptocurrency_id VARCHAR(50),
    symbol VARCHAR(10),
    name VARCHAR(100),
    price DECIMAL(20,8),
    change_24h DECIMAL(10,4),
    market_cap DECIMAL(30,2)
)
```

**Exemplo de Uso**:

```sql
SELECT * FROM public.get_top_gainers(10);
```

**Resposta**:

```
cryptocurrency_id | symbol | name     | price    | change_24h | market_cap
bitcoin          | BTC    | Bitcoin  | 45000.00 | 5.25       | 850000000000
ethereum         | ETH    | Ethereum | 3200.00  | 4.80       | 380000000000
...
```

---

### 5. `get_top_losers(limit_param)`

**Propósito**: Obtém as criptomoedas com maior perda nas últimas 24h

**Parâmetros**:

- `limit_param INTEGER DEFAULT 5` - Número de resultados

**Retorno**: Mesma estrutura de `get_top_gainers()`

**Exemplo de Uso**:

```sql
SELECT * FROM public.get_top_losers(5);
```

---

### 6. `update_latest_prices()`

**Propósito**: Atualiza a tabela `latest_prices` com os dados mais recentes

**Retorno**:

```sql
INTEGER -- Número de registros atualizados
```

**Exemplo de Uso**:

```sql
SELECT public.update_latest_prices();
```

**Resposta**:

```
update_latest_prices
150
```

---

## 💡 Exemplos de Uso

### No Backend FastAPI

```python
# Obter estatísticas de mercado
resultado = supabase.rpc('get_market_stats').execute()
stats = resultado.data[0] if resultado.data else {}

# Obter histórico de Bitcoin
historico = supabase.rpc('get_crypto_history', {
    'crypto_id_param': 'bitcoin',
    'days_param': 30
}).execute()

# Obter top 10 gainers
gainers = supabase.rpc('get_top_gainers', {
    'limit_param': 10
}).execute()
```

### No Frontend (via API)

```javascript
// Buscar estatísticas via API
const response = await fetch('/api/estatisticas');
const stats = await response.json();

// Buscar histórico de uma criptomoeda
const history = await fetch('/api/criptomoedas/bitcoin/historico?dias=30');
const data = await history.json();
```

## ⚠️ Tratamento de Erros

### Erros Comuns

1. **Função não encontrada**

   ```sql
   ERROR: function public.get_market_stats() does not exist
   ```

   **Solução**: Executar o script `schema.sql` no banco de dados

2. **Parâmetros inválidos**

   ```sql
   ERROR: invalid input syntax for type integer: "abc"
   ```

   **Solução**: Verificar tipos de parâmetros passados

3. **Permissões insuficientes**

   ```sql
   ERROR: permission denied for function get_market_stats
   ```

   **Solução**: Verificar configuração RLS e credenciais

### Fallbacks Implementados

O backend implementa fallbacks automáticos quando as funções RPC falham:

```python
try:
    resultado = supabase.rpc('get_market_stats').execute()
    stats = resultado.data[0]
except Exception as e:
    logger.warning(f"RPC falhou: {e}. Usando valores padrão.")
    stats = {"volume_24h": 100000000000, "market_cap": 2000000000000}
```

## 🔧 Manutenção

### Adicionando Nova Função RPC

1. **Criar função no schema.sql**:

```sql
CREATE OR REPLACE FUNCTION public.nova_funcao(param1 INTEGER)
RETURNS TABLE(resultado TEXT) AS $$
BEGIN
    RETURN QUERY SELECT 'exemplo'::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

2. **Atualizar documentação**
3. **Implementar no backend**
4. **Adicionar testes**

### Monitoramento

- **Logs**: Todas as chamadas RPC são logadas
- **Performance**: Tempo de execução monitorado
- **Erros**: Fallbacks automáticos implementados

## 📚 Referências

- [PostgreSQL Functions Documentation](https://www.postgresql.org/docs/current/sql-createfunction.html)
- [Supabase RPC Documentation](https://supabase.com/docs/guides/database/functions)
- [FastAPI Supabase Integration](https://github.com/supabase/supabase-py)
