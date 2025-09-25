// Tipos globais para o projeto

declare module 'next' {
  export interface Metadata {
    title?: string;
    description?: string;
  }
}

declare module 'next/link' {
  import { LinkHTMLAttributes } from 'react';
  export default function Link({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  } & LinkHTMLAttributes<HTMLAnchorElement>): JSX.Element;
}

declare module 'next/font/google' {
  export function Inter(options: {
    subsets: string[];
  }): {
    className: string;
  };
}

// Adicione outras declarações de tipo conforme necessário
