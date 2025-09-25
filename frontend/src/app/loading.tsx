export default function Loading() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      <span className="ml-4 text-gray-700 text-lg">Carregando...</span>
    </div>
  );
}
