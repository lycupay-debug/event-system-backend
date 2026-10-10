import type * as lark from "@larksuiteoapi/node-sdk";
import { createBitableMethods } from "../src/resources";

const methods = createBitableMethods({} as lark.Client);

methods.apps.get({ path: { app_token: "app_token" } });
methods.tables.list({ path: { app_token: "app_token" } });
methods.records.list({
  path: { app_token: "app_token", table_id: "table_id" },
  params: { page_size: 100 },
});

// @ts-expect-error app_token must be a string.
methods.apps.get({ path: { app_token: 123 } });

// @ts-expect-error record listing requires both app_token and table_id.
methods.records.list({ path: { app_token: "app_token" } });

async function responseTypesArePreserved(): Promise<void> {
  const response = await methods.records.list({
    path: { app_token: "app_token", table_id: "table_id" },
  });
  const apiCode: number | undefined = response.code;
  void apiCode;
}

void responseTypesArePreserved;
