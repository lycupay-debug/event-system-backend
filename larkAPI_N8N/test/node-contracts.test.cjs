const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const nodeFile = path.join(root, "nodes", "LarkBitable", "LarkBitable.node.ts");
const credentialFile = path.join(root, "credentials", "LarkBitableApi.credentials.ts");
const packageJson = require(path.join(root, "package.json"));

test("package declares the n8n node and credential entry points", () => {
  assert.equal(packageJson.n8n.nodes[0], "dist/nodes/LarkBitable/LarkBitable.node.js");
  assert.equal(packageJson.n8n.credentials[0], "dist/credentials/LarkBitableApi.credentials.js");
  assert.equal(packageJson.dependencies["@lycupay-debug/lark-api"], "file:../larkAPI");
});

test("node exposes all current Bitable resources and operations", () => {
  const source = fs.readFileSync(nodeFile, "utf8");
  const resources = [
    "apps", "tables", "records", "fields", "views", "forms",
    "fieldGroups", "dashboards", "roles", "workflows", "blockWorkflows",
  ];
  for (const resource of resources) assert.match(source, new RegExp(`value: "${resource}"`));
  const expectedOperations = [
    "batchCreateMembers", "batchDeleteMembers", "listFields", "updateField",
    "batchCreate", "batchGet", "batchUpdate", "batchDelete", "blockWorkflows",
  ];
  for (const operation of expectedOperations) {
    assert.ok(source.includes(`value: "${operation}"`), `missing operation ${operation}`);
  }
});

test("node delegates requests to larkAPI and does not embed secrets in parameters", () => {
  const source = fs.readFileSync(nodeFile, "utf8");
  assert.match(source, /createLarkClient/);
  assert.match(source, /createBitableMethods/);
  assert.match(source, /parsePayload\(this\.getNodeParameter\("payload", i\)\)/);
  assert.match(source, /continueOnFail\(\)/);
  assert.doesNotMatch(source, /appSecret.*type:\s*"string".*default:\s*["'][^"']+["']/s);
});

test("credential stores App Secret as a password field", () => {
  const source = fs.readFileSync(credentialFile, "utf8");
  assert.match(source, /name = "larkBitableApi"/);
  assert.match(source, /name: "appSecret"/);
  assert.match(source, /typeOptions:\s*\{ password: true \}/);
});
