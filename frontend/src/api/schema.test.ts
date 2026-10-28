import { describe, expect, it } from "vitest";
import { AGENT_EVENT_TYPES, AGENT_NAMES } from "./events";
import { EDGE_KINDS } from "./graph";
import schema from "./schema.json";

describe("TS mirror matches the backend schema (make schema)", () => {
  it("lists every event type", () => {
    const backendTypes = Object.keys(schema.AgentEvent.discriminator.mapping);
    expect([...AGENT_EVENT_TYPES].sort()).toEqual(backendTypes.sort());
  });

  it("lists every agent name", () => {
    expect([...AGENT_NAMES].sort()).toEqual([...schema.AgentEvent.$defs.AgentName.enum].sort());
  });

  it("lists every edge kind", () => {
    expect([...EDGE_KINDS].sort()).toEqual([...schema.RunGraph.$defs.EdgeKind.enum].sort());
  });
});
