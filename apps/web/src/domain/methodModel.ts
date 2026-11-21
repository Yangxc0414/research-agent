/**
 * Method-model projection (方法原模型, design/149).
 *
 * The method registry (modules/method-registry/registry.json, schema
 * ese-method-registry-0.1) is DATA, not code: ten shared governance slots ×
 * nine research methods, each declaring where it fits, its protocol fields,
 * artifacts, checks and what it cannot support. The CLI queries it via
 * research_agent/method_registry.py; `workspace export` ships the SAME file to
 * apps/web/public/method-registry.json, so this view consumes the identical
 * source. Nothing here edits the registry — a read-only projection.
 */

export interface MethodStageSlot {
  id: string;
  name: string;
}

export interface MethodGuideline {
  key: string;
  citation: string;
  mandates: string;
}

export interface MethodRegistryMethod {
  id: string;
  name_zh: string;
  name_en: string;
  fit_stages: string[];
  guidelines?: MethodGuideline[];
  protocol_fields: string[];
  threat_focus?: string[];
  artifacts: string[];
  cannot_support: string[];
  checks: Array<{ id: string; severity: string; requires?: string[] }>;
}

export interface MethodRegistryData {
  schema: string;
  boundary: string;
  stages: MethodStageSlot[];
  methods: MethodRegistryMethod[];
}

let cache: MethodRegistryData | null | undefined;

/** Fetch the exported registry snapshot (same file the CLI writes). Returns
 * null when it is missing — callers render an honest empty state. */
export async function loadMethodRegistry(): Promise<MethodRegistryData | null> {
  if (cache !== undefined) return cache;
  try {
    const response = await fetch("./method-registry.json", { cache: "no-cache" });
    if (!response.ok) throw new Error(String(response.status));
    const data = (await response.json()) as MethodRegistryData;
    cache = data.schema === "ese-method-registry-0.1" ? data : null;
  } catch {
    cache = null;
  }
  return cache;
}

/**
 * Which method profile each seeded session demonstrates. Declared here (not on
 * the task) because the demo sessions are frontend constants; a runtime task
 * should carry its method id in task metadata and bypass this map.
 */
export const SESSION_METHOD: Record<string, string> = {
  "ese-ms-20261118-03": "repository-mining",
  "e2e-closed-loop": "controlled-experiment",
  "full-chain-demo": "controlled-experiment"
};

export function methodForSession(
  taskId: string | undefined,
  registry: MethodRegistryData | null
): MethodRegistryMethod | null {
  if (!taskId || !registry) return null;
  const id = SESSION_METHOD[taskId];
  return id ? (registry.methods.find((m) => m.id === id) ?? null) : null;
}

/** fit map for the matrix: stage id -> the method declares activity there. */
export function fitMap(method: MethodRegistryMethod): Record<string, boolean> {
  const map: Record<string, boolean> = {};
  for (const stage of method.fit_stages) map[stage] = true;
  return map;
}

export function blockerCount(method: MethodRegistryMethod): number {
  return method.checks.filter((check) => check.severity === "blocker").length;
}
