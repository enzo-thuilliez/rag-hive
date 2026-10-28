import { useEffect, useState } from "react";
import { getHealth, type HealthResponse } from "../api/client";
import { config } from "../config";

/** Backend health as seen by the UI. */
export type HealthState =
  | { status: "loading" }
  | { status: "ok"; health: HealthResponse }
  | { status: "error"; message: string };

/** Poll `GET /health` every `pollMs` milliseconds and return the latest result. */
export function useHealth(pollMs: number = config.healthPollMs): HealthState {
  const [state, setState] = useState<HealthState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    const check = () => {
      getHealth(controller.signal).then(
        (health) => {
          setState({ status: "ok", health });
        },
        (error: unknown) => {
          if (controller.signal.aborted) return;
          setState({ status: "error", message: String(error) });
        },
      );
    };
    check();
    const timer = window.setInterval(check, pollMs);
    return () => {
      controller.abort();
      window.clearInterval(timer);
    };
  }, [pollMs]);

  return state;
}
