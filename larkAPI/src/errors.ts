export interface NormalizedLarkApiError {
  name: "LarkApiError";
  message: string;
  code?: number | string;
  requestId?: string;
  operation?: string;
  cause?: unknown;
}

export class LarkApiError extends Error {
  readonly code?: number | string;
  readonly requestId?: string;
  readonly operation?: string;
  readonly cause?: unknown;

  constructor(error: NormalizedLarkApiError) {
    super(error.message);
    this.name = error.name;
    this.code = error.code;
    this.requestId = error.requestId;
    this.operation = error.operation;
    this.cause = error.cause;
  }
}

/**
 * Normalizes SDK/API errors without logging credentials or request payloads.
 * The original error is retained as cause for diagnostic inspection.
 */
export function normalizeLarkApiError(
  error: unknown,
  operation?: string,
): LarkApiError {
  if (error instanceof LarkApiError) {
    return error;
  }

  const candidate =
    typeof error === "object" && error !== null
      ? (error as Record<string, unknown>)
      : {};

  const response =
    typeof candidate.response === "object" && candidate.response !== null
      ? (candidate.response as Record<string, unknown>)
      : {};

  const data =
    typeof response.data === "object" && response.data !== null
      ? (response.data as Record<string, unknown>)
      : {};

  const code = data.code ?? candidate.code;
  const requestId =
    (typeof data.request_id === "string" && data.request_id) ||
    (typeof candidate.requestId === "string" && candidate.requestId) ||
    undefined;

  const messageCandidate =
    data.msg ?? candidate.message ?? (typeof error === "string" ? error : undefined);

  return new LarkApiError({
    name: "LarkApiError",
    message:
      typeof messageCandidate === "string"
        ? messageCandidate
        : "Unknown Lark API error",
    ...(typeof code === "string" || typeof code === "number" ? { code } : {}),
    ...(requestId ? { requestId } : {}),
    ...(operation ? { operation } : {}),
    cause: error,
  });
}
