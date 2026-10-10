const test = require("node:test");
const assert = require("node:assert/strict");
const { LarkApiError, normalizeLarkApiError } = require("../dist/errors");

test("normalizes API response code, message, request ID, and operation", () => {
  const original = {
    response: {
      data: {
        code: 1254003,
        msg: "invalid app token",
        request_id: "req_test_123",
      },
    },
  };

  const error = normalizeLarkApiError(original, "bitable.app.get");

  assert.ok(error instanceof LarkApiError);
  assert.equal(error.code, 1254003);
  assert.equal(error.message, "invalid app token");
  assert.equal(error.requestId, "req_test_123");
  assert.equal(error.operation, "bitable.app.get");
  assert.equal(error.cause, original);
});

test("normalizes ordinary Error values without losing their message", () => {
  const error = normalizeLarkApiError(new Error("network failure"));

  assert.equal(error.message, "network failure");
  assert.equal(error.code, undefined);
  assert.equal(error.requestId, undefined);
});

test("normalizes non-object failures safely", () => {
  const error = normalizeLarkApiError("unknown failure", "bitable.record.list");

  assert.equal(error.message, "unknown failure");
  assert.equal(error.operation, "bitable.record.list");
});
