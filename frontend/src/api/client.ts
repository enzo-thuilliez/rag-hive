/** Typed HTTP client for the RAG Hive backend. */
import { config } from "../config";

/** Prefix of every backend route (`API_PREFIX` in `backend/src/rag_hive/api/__init__.py`). */
export const API_PREFIX = "/api";

/** Body of `GET /api/health`. Mirrors `HealthResponse` in `backend/src/rag_hive/api/health.py`. */
export interface HealthResponse {
  status: "ok";
  version: string;
}

/** A request to the backend failed: network error, non-2xx status or unexpected body. */
export class ApiError extends Error {
  /** HTTP status, or `null` when no response was received. */
  readonly status: number | null;

  /** Create an error for a failed backend call. */
  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Narrow an unknown JSON body to a `HealthResponse`. */
export function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== "object" || value === null) return false;
  const body = value as Record<string, unknown>;
  return body.status === "ok" && typeof body.version === "string";
}

/** GET `API_PREFIX + path` and return the parsed JSON body. */
async function getJson(path: string, signal?: AbortSignal): Promise<unknown> {
  const url = `${config.apiBaseUrl}${API_PREFIX}${path}`;
  let response: Response;
  try {
    response = await fetch(url, signal ? { signal } : {});
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(`GET ${url} failed: ${String(error)}`);
  }
  if (!response.ok) {
    throw new ApiError(`GET ${url} returned ${String(response.status)}`, response.status);
  }
  return (await response.json()) as unknown;
}

/** Fetch the backend health. Rejects with `ApiError` if it is unreachable or unhealthy. */
export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const body = await getJson("/health", signal);
  if (!isHealthResponse(body))
    throw new ApiError(`GET ${API_PREFIX}/health returned an unexpected body`);
  return body;
}
