import { useHealth } from "../hooks/useHealth";

const styles = {
  loading: "bg-slate-200 text-slate-600",
  ok: "bg-emerald-100 text-emerald-800",
  error: "bg-rose-100 text-rose-800",
} as const;

/** Header pill showing whether the backend answers `/health`. */
export function HealthBadge() {
  const health = useHealth();
  const label =
    health.status === "ok"
      ? `Backend OK · v${health.health.version}`
      : health.status === "error"
        ? "Backend unreachable"
        : "Checking backend…";

  return (
    <span
      role="status"
      title={health.status === "error" ? health.message : undefined}
      className={`rounded-full px-3 py-1 text-xs font-medium ${styles[health.status]}`}
    >
      {label}
    </span>
  );
}
