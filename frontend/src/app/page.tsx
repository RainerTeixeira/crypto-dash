import { redirect } from 'next/navigation';

export default function Home() {
  // Redireciona para a página do dashboard de criptomoedas
  redirect('/crypto-dash');
  
  // Este retorno nunca será alcançado, mas é necessário para o TypeScript
  return null;
}
