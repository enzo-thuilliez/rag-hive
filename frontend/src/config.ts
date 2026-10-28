/** Frontend runtime configuration, from `VITE_` variables in the repo-root `.env`. */

const DEFAULT_HEALTH_POLL_MS = 10_000;

function positiveInt(raw: string | undefined, fallback: number): number {
  const value = Number(raw);
  return raw && Number.isInteger(value) && value > 0 ? value : fallback;
}

/** Resolved configuration. Missing or empty variables fall back to their defaults. */
export const config = {
  /** Backend origin. Empty in dev: requests go to the Vite server, which proxies them. */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "",
  /** How often the header re-checks `/health`, in milliseconds. */
  healthPollMs: positiveInt(import.meta.env.VITE_HEALTH_POLL_MS, DEFAULT_HEALTH_POLL_MS),
} as const;
