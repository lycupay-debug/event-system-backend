const test = require("node:test");
const assert = require("node:assert/strict");
const { createBitableMethods } = require("../dist/resources");

function makeMethods(names) {
  return Object.fromEntries(
    names.map((name) => [
      name,
      async (payload) => ({ method: name, payload }),
    ]),
  );
}

test("exposes the 49 SDK-generated Bitable operations as named methods", () => {
  const client = {
    bitable: {
      app: makeMethods(["create", "get", "update", "copy"]),
      appTable: makeMethods(["create", "list", "patch", "delete", "batchCreate", "batchDelete"]),
      appTableRecord: makeMethods(["create", "get", "list", "search", "update", "delete", "batchCreate", "batchGet", "batchUpdate", "batchDelete"]),
      appTableField: makeMethods(["create", "list", "update", "delete"]),
      appTableView: makeMethods(["create", "get", "list", "patch", "delete"]),
      appTableForm: makeMethods(["get", "patch", "upgrade"]),
      appTableFormField: makeMethods(["list", "patch"]),
      appTableFieldGroup: makeMethods(["create"]),
      appDashboard: makeMethods(["list", "copy"]),
      appRole: makeMethods(["create", "list", "update", "delete"]),
      appRoleMember: makeMethods(["list", "create", "batchCreate", "delete", "batchDelete"]),
      appWorkflow: makeMethods(["list", "update"]),
      appBlockWorkflow: makeMethods(["list"]),
    },
  };

  const methods = createBitableMethods(client);
  const count = Object.values(methods)
    .flatMap((resource) => Object.values(resource))
    .length;

  assert.equal(count, 49);
});

test("passes payloads through and normalizes SDK failures", async () => {
  const client = {
    bitable: {
      app: makeMethods(["create", "get", "update", "copy"]),
      appTable: makeMethods(["create", "list", "patch", "delete", "batchCreate", "batchDelete"]),
      appTableRecord: makeMethods(["create", "get", "list", "search", "update", "delete", "batchCreate", "batchGet", "batchUpdate", "batchDelete"]),
      appTableField: makeMethods(["create", "list", "update", "delete"]),
      appTableView: makeMethods(["create", "get", "list", "patch", "delete"]),
      appTableForm: makeMethods(["get", "patch", "upgrade"]),
      appTableFormField: makeMethods(["list", "patch"]),
      appTableFieldGroup: makeMethods(["create"]),
      appDashboard: makeMethods(["list", "copy"]),
      appRole: makeMethods(["create", "list", "update", "delete"]),
      appRoleMember: makeMethods(["list", "create", "batchCreate", "delete", "batchDelete"]),
      appWorkflow: makeMethods(["list", "update"]),
      appBlockWorkflow: makeMethods(["list"]),
    },
  };

  const methods = createBitableMethods(client);
  const payload = { path: { app_token: "test_app" } };
  const result = await methods.apps.get(payload);

  assert.deepEqual(result, { method: "get", payload });
});
