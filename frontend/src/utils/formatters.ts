/**
 * Formats a numeric value as currency (USD)
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: value < 1 ? 8 : 2
  }).format(value);
}

/**
 * Formats a large number in compact format (e.g., 1.5M, 2.3B)
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1
  }).format(value);
}

/**
 * Formats a percentage
 */
export function formatPercentage(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value / 100);
}

/**
 * Formats a date for display
 */
export function formatDate(date: string): string {
  return new Date(date).toLocaleString('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Deprecated: Kept for backward compatibility
export const formatarMoeda = formatCurrency;
export const formatarNumero = formatNumber;
export const formatarPorcentagem = formatPercentage;
export const formatarData = formatDate;
