import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

// The repo-root .env is shared with the backend (see .env.example).
const repoRoot = path.resolve(import.meta.dirname, "..");

/** Read `key` from `env`, treating a missing or empty value as unset (same as the backend). */
function setting(env: Record<string, string | undefined>, key: string, fallback: string): string {
  const value = env[key];
  return value === undefined || value === "" ? fallback : value;
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, "");
  const backend = `http://${setting(env, "BACKEND_HOST", "127.0.0.1")}:${setting(env, "BACKEND_PORT", "8000")}`;

  return {
    plugins: [react(), tailwindcss()],
    envDir: repoRoot,
    server: {
      port: Number(setting(env, "FRONTEND_PORT", "5173")),
      strictPort: true,
      // Same-origin calls in dev: no CORS, and SSE streams through the proxy. The backend serves
      // only /api (ADR-004); every other path is the app's.
      proxy: {
        "/api": { target: backend, changeOrigin: true },
      },
    },
    test: {
      include: ["src/**/*.test.ts"],
    },
  };
});
