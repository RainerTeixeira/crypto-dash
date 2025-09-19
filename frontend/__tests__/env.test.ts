// Teste para verificar as variáveis de ambiente
// Este script verifica se todas as variáveis de ambiente necessárias estão definidas

import { describe } from "node:test";

describe('Variáveis de Ambiente', () => {
  // Lista de variáveis de ambiente que devem estar definidas
  const requiredEnvVars = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
    // Adicione aqui outras variáveis de ambiente necessárias
  ];

  requiredEnvVars.forEach(envVar => {
    test(`deve ter a variável ${envVar} definida`, () => {
      expect(process.env[envVar]).toBeDefined();
      expect(process.env[envVar]).not.toBe('');
    });
  });
});
