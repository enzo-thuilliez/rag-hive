import { NavLink, Outlet } from "react-router";
import { HealthBadge } from "./HealthBadge";

/** Run id the nav links point at until runs can be created from the Upload page. */
const PLACEHOLDER_RUN_ID = "example";

const links = [
  { to: "/", label: "Upload" },
  { to: `/runs/${PLACEHOLDER_RUN_ID}/map`, label: "Agent Map" },
  { to: `/runs/${PLACEHOLDER_RUN_ID}/results`, label: "Results" },
] as const;

/** App shell: title, navigation and backend health, above the current page. */
export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <div className="flex items-center gap-8">
          <span className="text-lg font-semibold">RAG Hive</span>
          <nav className="flex gap-4 text-sm">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end
                className={({ isActive }) =>
                  isActive ? "font-medium text-slate-900" : "text-slate-500 hover:text-slate-900"
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <HealthBadge />
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
