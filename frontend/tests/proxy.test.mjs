import assert from "node:assert/strict";
import test from "node:test";
import config from "../next.config.mjs";

test("same-origin API paths route to the internal FastAPI service", async () => {
  const previous = process.env.INTERNAL_API_BASE_URL;
  try {
    process.env.INTERNAL_API_BASE_URL = "http://backend:8000";
    assert.deepEqual(await config.rewrites(), [{
      source: "/api/v1/:path*", destination: "http://backend:8000/api/v1/:path*",
    }]);
    delete process.env.INTERNAL_API_BASE_URL;
    assert.equal((await config.rewrites())[0].destination,
      "http://127.0.0.1:8000/api/v1/:path*");
  } finally {
    if (previous === undefined) delete process.env.INTERNAL_API_BASE_URL;
    else process.env.INTERNAL_API_BASE_URL = previous;
  }
});
