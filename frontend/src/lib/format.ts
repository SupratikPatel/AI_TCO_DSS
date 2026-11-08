export type Currency = 'USD' | 'EUR';
export function money(value: number | null | undefined, currency: Currency, fx: number) {
  if (value == null) return 'Unavailable';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency, maximumFractionDigits: 0 }).format(currency === 'EUR' ? value / fx : value);
}
export function number(value: number | null | undefined, digits = 1) {
  return value == null ? 'Unavailable' : value.toLocaleString('en-US', { maximumFractionDigits: digits });
}
