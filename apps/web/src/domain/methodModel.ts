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

export interface MethodDimension {
  dimension: string;
  basis: string;
}

export interface TagVocabularyEntry {
  tag: string;
  definition: string;
  basis: string;
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
  /** design/153: the three reference-model dimensions. */
  inputs?: string[];
  evidence_sources?: string[];
  evaluation_dimensions?: MethodDimension[];
  /** Per-slot task cards from the registry (stage id -> task text). */
  stage_tasks?: Record<string, string>;
  /** design/155: vocabulary tags from the 标签化梳理 todo. */
  tags?: string[];
}

export interface MethodRegistryData {
  schema: string;
  boundary: string;
  stages: MethodStageSlot[];
  methods: MethodRegistryMethod[];
  /** design/155: shared tag vocabulary (tag -> definition + basis). */
  tag_vocabulary?: TagVocabularyEntry[];
  /** design/156: the element port model + reference wirings (framework as data). */
  elements?: Array<{
    id: string;
    label: string;
    input_kinds: string[];
    outputs: Array<{ consumes: string | null; produces: string }>;
    human: boolean;
  }>;
  compositions?: Array<{
    id: string;
    label: string;
    sub: string;
    wiring: Array<{ element: string; consumes: string | null }>;
  }>;
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
    cache = data.schema === "ese-method-registry-0.4" ? data : null;
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

/**
 * 证据类型与效力边界 per method (design/152).
 *
 * The classification is the standard empirical-methodology one (Easterbrook et
 * al. 2008, "Selecting Empirical Methods for Software Engineering Research";
 * Creswell, Research Design): each method produces a DIFFERENT KIND of
 * evidence, which is exactly why their inputs/outputs/validity differ. Every
 * validity limit below is verbatim from the registry's own cannot_support /
 * threat_focus fields — the kind label is the display-level classification.
 */
export interface EvidenceProfile {
  kind: string;
  /** 依据（文献） */
  basis: string;
}

export const EVIDENCE_PROFILES: Record<string, EvidenceProfile> = {
  "controlled-experiment": {
    kind: "一手受控测量（受控 + 随机）",
    basis: "Wohlin 2014；实验的内部效度来自控制与随机化"
  },
  "quasi-experiment": {
    kind: "一手分组观察（有对照，无随机）",
    basis: "因果主张受识别策略限制"
  },
  "benchmark-evaluation": {
    kind: "标准化任务测量",
    basis: "可复现，但受污染与饱和威胁"
  },
  "repository-mining": {
    kind: "回顾性观察挖掘",
    basis: "生态效度好；标签为启发式，因果机制不可支持"
  },
  "systematic-literature-review": {
    kind: "二手综合（证据 = 已发表研究）",
    basis: "Kitchenham 2007 / PRISMA 2020；效力取决于检索与筛选的可复现性"
  },
  "case-study": {
    kind: "个案深描与三角验证",
    basis: "Runeson & Höst 2009；深度与机制，不可统计泛化"
  },
  survey: {
    kind: "自报测量（问卷/访谈）",
    basis: "主观体验可测，行为因果不可支持"
  },
  "design-science": {
    kind: "设计制品评估",
    basis: "效用主张限于评估策略所及"
  },
  "action-research": {
    kind: "介入循环反思",
    basis: "情境性知识；无介入则不可归因"
  }
};

export function evidenceProfileFor(methodId: string): EvidenceProfile | null {
  return EVIDENCE_PROFILES[methodId] ?? null;
}

/**
 * 标签化梳理的提取结果（design/155）：tags held by >=3 methods are
 * commonalities, ==2 partial, ==1 essential differences — the advisor's
 * "提炼共性、识别本质差异" as reproducible data.
 */
export type TagGroup = "common" | "partial" | "difference";

export interface TagAnalysisRow {
  tag: string;
  definition: string;
  basis: string;
  methods: string[];
  group: TagGroup;
}

export function tagAnalysis(registry: MethodRegistryData): TagAnalysisRow[] {
  const defs = new Map((registry.tag_vocabulary ?? []).map((entry) => [entry.tag, entry]));
  const counter = new Map<string, string[]>();
  for (const method of registry.methods) {
    for (const tag of method.tags ?? []) {
      const list = counter.get(tag) ?? [];
      list.push(method.id);
      counter.set(tag, list);
    }
  }
  const rows: TagAnalysisRow[] = [];
  for (const [tag, methods] of counter) {
    const group: TagGroup = methods.length >= 3 ? "common" : methods.length === 2 ? "partial" : "difference";
    const def = defs.get(tag);
    rows.push({
      tag,
      definition: def?.definition ?? "",
      basis: def?.basis ?? "",
      methods: [...methods].sort(),
      group
    });
  }
  return rows.sort((a, b) => b.methods.length - a.methods.length || a.tag.localeCompare(b.tag));
}
