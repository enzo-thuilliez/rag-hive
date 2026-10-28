/** Any JSON value. Mirrors pydantic's `JsonValue`. */
export type JsonValue =
  string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };
