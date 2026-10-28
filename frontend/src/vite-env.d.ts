/// <reference types="vite/client" />

/** Frontend variables read from the repo-root `.env` (only `VITE_`-prefixed ones are exposed). */
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_HEALTH_POLL_MS?: string;
}

/** Vite's `import.meta`, narrowed to this app's env. */
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
