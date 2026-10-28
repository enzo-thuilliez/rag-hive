/**
 * Agent workflow topology returned by `GET /api/runs/{runId}/graph`.
 *
 * Mirrors `backend/src/rag_hive/agents/topology.py`, checked by `schema.test.ts`.
 */
import type { AgentName } from "./events";

/** Edge kinds: a handoff, or a fan-out into / fan-in out of the parallel workers. */
export const EDGE_KINDS = ["handoff", "fan_out", "fan_in"] as const;

/** One edge kind. */
export type EdgeKind = (typeof EDGE_KINDS)[number];

/** One agent role on the map. */
export interface GraphNode {
  id: string;
  agent: AgentName;
  label: string;
  /** True when the node stands for a variable number of runtime instances (workers). */
  dynamic: boolean;
}

/** A directed connection between two nodes. */
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
}

/** Nodes and edges of a run's workflow. */
export interface RunGraph {
  runId: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}
