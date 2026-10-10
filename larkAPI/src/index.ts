/**
 * Public entry point for the Lark Bitable API method library.
 * Resource methods are SDK-backed; see API_COVERAGE.md for endpoint coverage
 * and verification status.
 */
export { createLarkClient, type LarkClientConfig } from "./client";
export { LarkApiError, normalizeLarkApiError } from "./errors";
export {
  createBitableMethods,
  createBitableAttachmentMethods,
  type BitableMethods,
  type BitableAttachmentMethods,
} from "./resources";
export {
  collectCursorPages,
  type CollectPagesOptions,
  type CollectedPages,
  type CursorPage,
} from "./pagination";
