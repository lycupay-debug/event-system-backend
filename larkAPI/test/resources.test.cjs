const test = require("node:test");
const assert = require("node:assert/strict");
const { createBitableMethods, createBitableAttachmentMethods } = require("../dist/resources");
const { LarkApiError } = require("../dist/errors");

const sdkResources = {
  app: ["create", "get", "update", "copy"],
  appTable: ["create", "list", "patch", "delete", "batchCreate", "batchDelete"],
  appTableRecord: ["create", "get", "list", "search", "update", "delete", "batchCreate", "batchGet", "batchUpdate", "batchDelete"],
  appTableField: ["create", "list", "update", "delete"],
  appTableView: ["create", "get", "list", "patch", "delete"],
  appTableForm: ["get", "patch", "upgrade"],
  appTableFormField: ["list", "patch"],
  appTableFieldGroup: ["create"],
  appDashboard: ["list", "copy"],
  appRole: ["create", "list", "update", "delete"],
  appRoleMember: ["list", "create", "batchCreate", "delete", "batchDelete"],
  appWorkflow: ["list", "update"],
  appBlockWorkflow: ["list"],
};

function makeMethods(resource, names, calls, failingMethod) {
  return Object.fromEntries(names.map((name) => [
    name,
    async function (payload) {
      calls.push({ resource, name, payload, ownerMarker: this.marker });
      if (failingMethod === `${resource}.${name}`) {
        throw { response: { data: { code: 1254003, msg: "mock failure", request_id: "req-test-1" } } };
      }
      return { resource, name, payload, ownerMarker: this.marker };
    },
  ]));
}

function makeClient(failingMethod) {
  const calls = [];
  const bitable = Object.fromEntries(
    Object.entries(sdkResources).map(([resource, names]) => [
      resource,
      Object.assign(
        makeMethods(resource, names, calls, failingMethod),
        { marker: resource },
      ),
    ]),
  );
  return { client: { bitable }, calls };
}

test("exposes all 49 SDK-generated Bitable operations as named methods", () => {
  const { client } = makeClient();
  const methods = createBitableMethods(client);
  const count = Object.values(methods)
    .flatMap((resource) => Object.values(resource))
    .length;

  assert.equal(count, 49);
  assert.deepEqual(Object.keys(methods).sort(), [
    "apps", "blockWorkflows", "dashboards", "fieldGroups", "fields",
    "forms", "records", "roles", "tables", "views", "workflows",
  ].sort());
});

test("every named wrapper forwards its payload to an SDK method", async () => {
  const { client, calls } = makeClient();
  const methods = createBitableMethods(client);
  let count = 0;

  for (const [resourceName, resource] of Object.entries(methods)) {
    for (const [methodName, method] of Object.entries(resource)) {
      const payload = { marker: `${resourceName}.${methodName}`, path: { app_token: "test_app" } };
      const result = await method(payload);
      assert.equal(result.payload, payload);
      assert.equal(result.ownerMarker, calls[count].resource);
      assert.equal(calls[count].ownerMarker, calls[count].resource);
      assert.equal(calls[count].payload, payload);
      count += 1;
    }
  }

  assert.equal(count, 49);
  assert.equal(calls.length, 49);
});

test("normalizes an SDK failure with the correct wrapper operation", async () => {
  const { client } = makeClient("app.get");
  const methods = createBitableMethods(client);

  await assert.rejects(
    methods.apps.get({ path: { app_token: "test_app" } }),
    (error) => {
      assert.ok(error instanceof LarkApiError);
      assert.equal(error.operation, "bitable.app.get");
      assert.equal(error.code, 1254003);
      assert.equal(error.message, "mock failure");
      assert.equal(error.requestId, "req-test-1");
      return true;
    },
  );
});

test("exposes supporting Drive media methods for Bitable attachments", async () => {
  const calls = [];
  const names = [
    "uploadAll",
    "uploadPrepare",
    "uploadPart",
    "uploadFinish",
    "download",
    "batchGetTmpDownloadUrl",
  ];
  const media = Object.fromEntries(names.map((name) => [
    name,
    async (payload) => {
      calls.push({ name, payload });
      return { name, payload };
    },
  ]));
  const methods = createBitableAttachmentMethods({ drive: { media } });
  const payload = {
    data: {
      file_name: "attachment.txt",
      parent_type: "bitable_file",
      parent_node: "test_app_token",
      size: 1,
      file: Buffer.from("x"),
    },
  };
  const result = await methods.upload(payload);

  assert.equal(result.name, "uploadAll");
  assert.equal(result.payload, payload);
  assert.equal(calls[0].payload, payload);
  assert.equal(Object.keys(methods).length, 6);
});

test("normalizes attachment upload failures with Drive operation context", async () => {
  const media = {
    uploadAll: async () => {
      throw { response: { data: { code: 1254001, msg: "bad attachment", request_id: "req-file-1" } } };
    },
  };
  const methods = createBitableAttachmentMethods({ drive: { media } });

  await assert.rejects(
    methods.upload({ data: {} }),
    (error) => {
      assert.ok(error instanceof LarkApiError);
      assert.equal(error.operation, "drive.media.uploadAll");
      assert.equal(error.code, 1254001);
      assert.equal(error.requestId, "req-file-1");
      return true;
    },
  );
});
