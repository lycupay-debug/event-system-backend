const test = require("node:test");
const assert = require("node:assert/strict");
const { collectCursorPages } = require("../dist/pagination");

test("collects cursor pages and passes the continuation token", async () => {
  const calls = [];
  const pages = [
    { data: { items: [1, 2], has_more: true, page_token: "next-a" } },
    { data: { items: [3], has_more: true, page_token: "next-b" } },
    { data: { items: [4], has_more: false } },
  ];

  const result = await collectCursorPages(async (token) => {
    calls.push(token);
    return pages[calls.length - 1];
  });

  assert.deepEqual(result, { items: [1, 2, 3, 4], pagesFetched: 3 });
  assert.deepEqual(calls, [undefined, "next-a", "next-b"]);
});

test("fails if has_more is true without a continuation token", async () => {
  await assert.rejects(
    () => collectCursorPages(async () => ({ data: { items: [], has_more: true } })),
    /without a page_token/,
  );
});

test("fails safely when the server repeats a cursor", async () => {
  await assert.rejects(
    () => collectCursorPages(async () => ({
      data: { items: [], has_more: true, page_token: "same-token" },
    })),
    /repeated page_token/,
  );
});

test("enforces a positive maxPages limit", async () => {
  await assert.rejects(
    () => collectCursorPages(async () => ({ data: { items: [], has_more: false } }), { maxPages: 0 }),
    /maxPages must be a positive integer/,
  );
});
