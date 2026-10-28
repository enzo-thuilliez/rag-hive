/**
 * Agent events streamed over SSE by `GET /api/runs/{runId}/events`.
 *
 * Mirrors `backend/src/rag_hive/events/schema.py`. `schema.test.ts` checks these against the
 * exported `schema.json`; change both sides in the same commit.
 */
import type { JsonValue } from "./json";

/** Agent roles, in workflow order. */
export const AGENT_NAMES = [
  "profiler",
  "planner",
  "qa_generator",
  "worker",
  "judge",
  "reporter",
] as const;

/** One agent role. */
export type AgentName = (typeof AGENT_NAMES)[number];

/** Envelope shared by every event. */
export interface BaseEvent {
  runId: string;
  /** Per-run sequence number, strictly increasing. Also the SSE `id`. */
  seq: number;
  /** ISO 8601 timestamp with timezone. */
  timestamp: string;
  agent: AgentName;
  /** Distinguishes instances of a role, e.g. `worker-3`. */
  agentInstanceId: string | null;
  /** Instance (or role, for singletons) that spawned this agent. */
  parentInstanceId: string | null;
}

/** An agent began working. */
export interface AgentStartedEvent extends BaseEvent {
  type: "agent_started";
  task: string;
}

/** An agent called a tool. */
export interface ToolCallEvent extends BaseEvent {
  type: "tool_call";
  tool: string;
  arguments: Record<string, JsonValue>;
}

/** Intermediate progress of a long step. */
export interface ProgressEvent extends BaseEvent {
  type: "progress";
  message: string;
  /** Completion between 0 and 1, when known. */
  fraction: number | null;
}

/** An agent produced its output. */
export interface ResultEvent extends BaseEvent {
  type: "result";
  summary: string;
  data: Record<string, JsonValue>;
}

/** An agent passed control to another. */
export interface HandoffEvent extends BaseEvent {
  type: "handoff";
  toAgent: AgentName;
  toInstanceId: string | null;
  reason: string;
}

/** An agent failed. */
export interface ErrorEvent extends BaseEvent {
  type: "error";
  message: string;
  recoverable: boolean;
}

/** Any agent event, discriminated by `type`. */
export type AgentEvent =
  AgentStartedEvent | ToolCallEvent | ProgressEvent | ResultEvent | HandoffEvent | ErrorEvent;

/** The `type` of an agent event. Also its SSE event name. */
export type AgentEventType = AgentEvent["type"];

// A Record must name every key of the union, so adding an event type without listing it here
// fails to compile.
const eventTypes: Record<AgentEventType, true> = {
  agent_started: true,
  tool_call: true,
  progress: true,
  result: true,
  handoff: true,
  error: true,
};

/** Every event type, for registering one `EventSource` listener per type. */
export const AGENT_EVENT_TYPES = Object.keys(eventTypes) as readonly AgentEventType[];
