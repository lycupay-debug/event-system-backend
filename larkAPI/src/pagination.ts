export interface CursorPage<T> {
  data?: {
    items?: T[];
    has_more?: boolean;
    page_token?: string;
    [key: string]: unknown;
  };
}

export interface CollectPagesOptions {
  /** Safety limit against a broken cursor or unexpected server response. */
  maxPages?: number;
}

export interface CollectedPages<T> {
  items: T[];
  pagesFetched: number;
}

/**
 * Collects every page from a cursor-based Lark API list operation.
 *
 * Pass a callback that retains all original query parameters and substitutes
 * only page_token. The helper does not retry writes and is intended for read
 * operations whose API contract documents cursor pagination.
 */
export async function collectCursorPages<T>(
  fetchPage: (pageToken?: string) => Promise<CursorPage<T>>,
  options: CollectPagesOptions = {},
): Promise<CollectedPages<T>> {
  const maxPages = options.maxPages ?? 1000;
  if (!Number.isInteger(maxPages) || maxPages < 1) {
    throw new Error("maxPages must be a positive integer");
  }

  const items: T[] = [];
  const seenTokens = new Set<string>();
  let pageToken: string | undefined;
  let pagesFetched = 0;

  while (pagesFetched < maxPages) {
    const page = await fetchPage(pageToken);
    pagesFetched += 1;
    items.push(...(page.data?.items ?? []));

    if (!page.data?.has_more) {
      return { items, pagesFetched };
    }

    const nextToken = page.data.page_token;
    if (!nextToken) {
      throw new Error("Lark API returned has_more=true without a page_token");
    }
    if (seenTokens.has(nextToken) || nextToken === pageToken) {
      throw new Error("Lark API returned a repeated page_token");
    }

    seenTokens.add(nextToken);
    pageToken = nextToken;
  }

  throw new Error(`Pagination exceeded maxPages (${maxPages})`);
}
