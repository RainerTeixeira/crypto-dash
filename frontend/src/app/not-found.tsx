import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-4">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md text-center">
        <h2 className="text-4xl font-bold text-gray-800 mb-4">404</h2>
        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Página não encontrada</h3>
        <p className="text-gray-600 mb-6">
          A página que você está procurando não existe ou foi movida.
        </p>
        <Link 
          href="/crypto-dash"
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors inline-block"
        >
          Voltar para o Dashboard
        </Link>
      </div>
    </div>
  );
}
