    async def update_market_stats(self, data: List[Dict[str, Any]]) -> None:
        """
        📊 Atualiza estatísticas globais de mercado no Redis.
        
        Calcula métricas agregadas como capitalização de mercado total, volume de 24h,
        número de criptomoedas ativas e distribuição por capitalização. Essas estatísticas
        são então armazenadas no Redis para acesso rápido.
        
        Args:
            data (List[Dict[str, Any]]): A lista de dicionários com os dados brutos das criptomoedas.
        """
        if not redis_client: # Garante que o cliente Redis esteja inicializado.
            logger.error("❌ Cliente Redis não inicializado. Não foi possível atualizar as estatísticas de mercado.")
            return

        try:
            logger.info("🔄 Calculando e atualizando estatísticas globais de mercado...")

            # 1. Calcula estatísticas agregadas a partir dos dados extraídos.
            total_market_cap = sum(item.get('market_cap', 0) for item in data if item.get('market_cap'))
            total_volume_24h = sum(item.get('total_volume', 0) for item in data if item.get('total_volume'))
            active_cryptocurrencies = len([item for item in data if item.get('market_cap', 0) > 0])

            # 2. Calcula a distribuição de capitalização de mercado.
            market_cap_distribution = {
                'large_cap': len([item for item in data if item.get('market_cap', 0) > 10000000000]),  # > $10 bilhões
                'mid_cap': len([item for item in data if 1000000000 < item.get('market_cap', 0) <= 10000000000]),  # $1 bilhão - $10 bilhões
                'small_cap': len([item for item in data if 0 < item.get('market_cap', 0) <= 1000000000])  # $0 - $1 bilhão
            }

            # 3. Monta o dicionário de estatísticas de mercado.
            market_stats = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'active_cryptocurrencies': active_cryptocurrencies,
                'total_market_cap_usd': total_market_cap,
                'total_volume_usd_24h': total_volume_24h,
                'market_cap_percentage': market_cap_distribution,
                'markets': 1
            }

            # 4. Armazena as estatísticas no Redis
            stats_key = f"{REDIS_KEY_PREFIX}market:stats"
            success = await self._store_in_redis({
                stats_key: json.dumps(market_stats)
            })

            if success:
                logger.info("✅ Estatísticas globais de mercado atualizadas com sucesso no Redis.")
            else:
                logger.error("❌ Falha ao atualizar as estatísticas de mercado no Redis.")

        except Exception as e: # Captura e registra qualquer erro durante a atualização das estatísticas.
            logger.warning(f"⚠️ Erro inesperado ao calcular/atualizar market_stats: {e}", exc_info=True)
