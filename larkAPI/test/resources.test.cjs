const test = require("node:test");
const assert = require("node:assert/strict");
const { createBitableMethods } = require("../dist/resources");
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
    async (payload) => {
      calls.push({ resource, name, payload });
      if (failingMethod === `${resource}.${name}`) {
        throw { code: 1254003, msg: "mock failure", request_id: "req-test-1" };
      }
      return { resource, name, payload };
    },
  ]));
}

function makeClient(failingMethod) {
  const calls = [];
  const bitable = Object.fromEntries(
    Object.entries(sdkResources).map(([resource, names]) => [
      resource,
      makeMethods(resource, names, calls, failingMethod),
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
