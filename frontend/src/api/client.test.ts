import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, getHealth } from "./client";

function stubFetch(impl: () => Promise<Response>) {
  const fetchMock = vi.fn(impl);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("getHealth", () => {
  it("returns the health body", async () => {
    const fetchMock = stubFetch(() =>
      Promise.resolve(Response.json({ status: "ok", version: "0.1.0" })),
    );

    await expect(getHealth()).resolves.toEqual({ status: "ok", version: "0.1.0" });
    expect(fetchMock).toHaveBeenCalledWith("/api/health", {});
  });

  it("rejects with the status on a non-2xx response", async () => {
    stubFetch(() => Promise.resolve(new Response("down", { status: 503 })));

    await expect(getHealth()).rejects.toMatchObject({ name: "ApiError", status: 503 });
  });

  it("rejects on an unexpected body", async () => {
    stubFetch(() => Promise.resolve(Response.json({ status: "maybe" })));

    await expect(getHealth()).rejects.toBeInstanceOf(ApiError);
  });

  it("rejects with a null status when the network fails", async () => {
    stubFetch(() => Promise.reject(new TypeError("fetch failed")));

    await expect(getHealth()).rejects.toMatchObject({ name: "ApiError", status: null });
  });
});
