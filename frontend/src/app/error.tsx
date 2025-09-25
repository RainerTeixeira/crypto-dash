'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log do erro para um serviço de relatórios
    console.error('Erro na aplicação:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md text-center">
        <h2 className="text-2xl font-bold text-red-600 mb-4">
          Ocorreu um erro inesperado
        </h2>
        <p className="text-gray-700 mb-6">
          Desculpe, algo deu errado. Por favor, tente novamente mais tarde.
        </p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          Tentar novamente
        </button>
        <p className="mt-4 text-sm text-gray-500">
          Se o problema persistir, entre em contato com o suporte.
        </p>
      </div>
    </div>
  );
}
