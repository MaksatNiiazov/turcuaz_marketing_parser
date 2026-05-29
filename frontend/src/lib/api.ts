import type {
  CategoryStats,
  MarketProduct,
  ParserCategory,
  ParserRun,
  ParserSource,
  ProductSnapshot,
  ProductStats,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...init.headers,
    },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || data?.message || `HTTP ${response.status}`);
  }
  return data as T;
}

function params(values: Record<string, string | number | boolean | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== null && value !== '') search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : '';
}

export function fetchSources(): Promise<ParserSource[]> {
  return requestJson<ParserSource[]>('/api/v1/market-parser/sources');
}

export function createSource(payload: {
  name: string;
  code: string;
  base_url: string;
  type: string;
  is_active: boolean;
}): Promise<ParserSource> {
  return requestJson<ParserSource>('/api/v1/market-parser/sources', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchCategories(sourceId?: number): Promise<ParserCategory[]> {
  return requestJson<ParserCategory[]>(
    `/api/v1/market-parser/categories${params({ source_id: sourceId })}`,
  );
}

export function syncCategories(sourceId: number): Promise<ParserCategory[]> {
  return requestJson<ParserCategory[]>('/api/v1/market-parser/categories/sync', {
    method: 'POST',
    body: JSON.stringify({ source_id: sourceId }),
  });
}

export function setCategoryEnabled(categoryId: number, enabled: boolean): Promise<ParserCategory> {
  return requestJson<ParserCategory>(
    `/api/v1/market-parser/categories/${categoryId}/${enabled ? 'enable' : 'disable'}`,
    { method: 'PATCH' },
  );
}

export function startRun(payload: {
  source_id: number;
  category_ids: number[];
  parse_all_enabled: boolean;
  created_by?: string;
}): Promise<ParserRun> {
  return requestJson<ParserRun>('/api/v1/market-parser/runs', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function fetchRuns(sourceId?: number): Promise<ParserRun[]> {
  return requestJson<ParserRun[]>(`/api/v1/market-parser/runs${params({ source_id: sourceId })}`);
}

export function fetchRun(runId: number): Promise<ParserRun> {
  return requestJson<ParserRun>(`/api/v1/market-parser/runs/${runId}`);
}

export function fetchProducts(filters: {
  source_id?: number;
  category_id?: number;
  name?: string;
  sku?: string;
  has_discount?: boolean;
  is_available?: boolean;
}): Promise<MarketProduct[]> {
  return requestJson<MarketProduct[]>(`/api/v1/market-parser/products${params(filters)}`);
}

export function fetchProductSnapshots(
  productId: number,
  filters: { from?: string; to?: string } = {},
): Promise<ProductSnapshot[]> {
  return requestJson<ProductSnapshot[]>(
    `/api/v1/market-parser/products/${productId}/snapshots${params(filters)}`,
  );
}

export function fetchProductStats(
  productId: number,
  filters: { from?: string; to?: string } = {},
): Promise<ProductStats> {
  return requestJson<ProductStats>(
    `/api/v1/market-parser/products/${productId}/stats${params(filters)}`,
  );
}

export function fetchCategoryStats(
  categoryId: number,
  filters: { from?: string; to?: string } = {},
): Promise<CategoryStats> {
  return requestJson<CategoryStats>(
    `/api/v1/market-parser/categories/${categoryId}/stats${params(filters)}`,
  );
}

export function exportUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}
