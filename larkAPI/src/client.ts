import * as lark from "@larksuiteoapi/node-sdk";

export interface LarkClientConfig {
  appId: string;
  appSecret: string;
  /** "feishu" for Feishu CN; "lark" for Lark global. */
  platform?: "feishu" | "lark";
  /** Optional request timeout in milliseconds. */
  timeout?: number;
}

/**
 * Creates the official SDK client used by all resource wrappers.
 * Credentials must be supplied by the caller (for example, environment variables);
 * this package never reads or stores secrets implicitly.
 */
export function createLarkClient(config: LarkClientConfig): lark.Client {
  if (!config.appId?.trim()) {
    throw new Error("LarkClientConfig.appId is required");
  }
  if (!config.appSecret?.trim()) {
    throw new Error("LarkClientConfig.appSecret is required");
  }

  return new lark.Client({
    appId: config.appId,
    appSecret: config.appSecret,
    domain: config.platform === "lark" ? lark.Domain.Lark : lark.Domain.Feishu,
    ...(config.timeout ? { loggerLevel: lark.LoggerLevel.error } : {}),
  });
}
