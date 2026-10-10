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
  assert.equal(packageJson.devDependencies["@lycupay-debug/lark-api"], "file:../larkAPI");
  assert.equal(packageJson.dependencies["@larksuiteoapi/node-sdk"], "1.72.0");
  assert.ok(packageJson.scripts.build.includes("esbuild nodes/LarkBitable/LarkBitable.node.ts"));
});

test("node exposes all current Bitable resources and 49 operations", () => {
  const source = fs.readFileSync(nodeFile, "utf8");
  const resources = [
    "apps", "tables", "records", "fields", "views", "forms",
    "fieldGroups", "dashboards", "roles", "workflows", "blockWorkflows", "attachments",
  ];
  for (const resource of resources) assert.match(source, new RegExp(`value: "${resource}"`));
  const expectedOperations = [
    "batchCreateMembers", "batchDeleteMembers", "listFields", "updateField",
    "batchCreate", "batchGet", "batchUpdate", "batchDelete", "blockWorkflows",
    "upload", "prepareUpload", "uploadPart", "finishUpload", "download", "batchGetTmpDownloadUrl",
  ];
  const operationsBlock = source.split("const RESOURCE_OPERATIONS")[1].split("const RESOURCE_NAMES")[0];
  const allOperationValues = [...operationsBlock.matchAll(/value: "[A-Za-z]+"/g)];
  assert.equal(allOperationValues.length, 55);
  const attachmentBlock = operationsBlock.split("attachments: [")[1];
  assert.equal([...attachmentBlock.matchAll(/value: "[A-Za-z]+"/g)].length, 6);
  assert.equal(allOperationValues.length - 6, 49);
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

test("attachment operations support n8n binary upload and download", () => {
  const source = fs.readFileSync(nodeFile, "utf8");
  assert.match(source, /createBitableAttachmentMethods/);
  assert.match(source, /getBinaryDataBuffer\(i, binaryPropertyName\)/);
  assert.match(source, /prepareBinaryData\(/);
  assert.match(source, /outputBinaryPropertyName/);
  assert.match(source, /responseToBuffer/);
});

test("credential stores App Secret as a password field", () => {
  const source = fs.readFileSync(credentialFile, "utf8");
  assert.match(source, /name = "larkBitableApi"/);
  assert.match(source, /name: "appSecret"/);
  assert.match(source, /typeOptions:\s*\{ password: true \}/);
});
