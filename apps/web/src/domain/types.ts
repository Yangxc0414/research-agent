export type Mode = "research" | "experiment" | "writing" | "auto";
export type AccessMode = "read_only" | "ask" | "full";
export type ContextTab = "run" | "evidence" | "evolution" | "eval";
export type SettingsSection =
  | "general"
  | "appearance"
  | "shortcuts"
  | "model"
  | "memory"
  | "agents"
  | "commands"
  | "plugins"
  | "evolution"
  | "runtime"
  | "usage"
  | "lineage"
  | "archive"
  | "data"
  | "guide"
  | "about";
export type TaskStatus = "active" | "blocked" | "done";
export type GateStatus = "pass" | "needs_human" | "pending" | "not_started" | "blocked";
export type StageStatus = "pending" | "running" | "done" | "waiting" | "skipped";

export interface WorkspaceFolder {
  name: string;
  files: number;
  bytes: number;
  importedAt: string;
}

export interface ContextAttachment {
  id: string;
  kind: "file" | "folder";
  name: string;
  source: "local" | "workspace";
  files: number;
  bytes: number;
  note?: string;
}

export interface WorkspaceFileEntry {
  path: string;
  name: string;
  size: number;
  lastModified: number;
  extension: string;
  handle?: FileSystemFileHandle;
  file?: File;
}

export interface WorkspaceFileScan {
  name: string;
  entries: WorkspaceFileEntry[];
  bytes: number;
  truncated: boolean;
  source: "handle" | "files";
}

export interface Workspace {
  id: string;
  name: string;
  note: string;
  folder?: WorkspaceFolder;
}

export type SkillSource = "builtin" | "custom" | "imported";

export interface ReviewFinding {
  id: string;
  reviewer: string;
  check: string;
  label: string;
  status: "pass" | "warn" | "deferred" | "blocked";
  summary: string;
}

export interface ReviewPackResult {
  id: string;
  generatedAt: string;
  reviewers: number;
  findings: ReviewFinding[];
  summary: string;
  note: string;
}
export type SkillActivation = "auto" | "manual" | "off";

export interface Skill {
  id: string;
  name: string;
  description: string;
  instructions: string;
  tools: string[];
  activation: SkillActivation;
  source: SkillSource;
  version: string;
  createdAt?: string;
  origin?: string;
  license?: string;
}

export interface SkillDraft {
  name: string;
  description: string;
  instructions: string;
  tools: string[];
  origin?: string;
}

export type PermissionKind = "start_auto" | "step_auto" | "run_experiment" | "approve_candidate" | "approve_tool";

export interface PermissionRequest {
  id: string;
  kind: PermissionKind;
  taskId: string;
  title: string;
  detail: string;
  targetId?: string;
}

export interface Gate {
  id: string;
  status: GateStatus;
  reason: string;
}

export interface Coverage {
  sources: number;
  spans: number;
  gaps: number;
  abstractOnly: number;
}

export interface EvidenceItem {
  id: string;
  kind: "gap" | "hypothesis" | "claim";
  status: "open" | "candidate" | "unsigned" | "signed" | "blocked";
  text: string;
  scope: string;
  refs: string[];
  note?: string;
}

export interface Protocol {
  hypothesis: string;
  baseline: string;
  metric: string;
  seeds: number;
  controls: string[];
}

export interface RunRecord {
  id: string;
  dataset: string;
  seeds: number;
  metric: string;
  mean: number;
  baseline: number;
  ea: string;
  status: string;
}

export interface AutomationPlanStage {
  id: string;
  label: string;
  owner: string;
  gates: string[];
  human_gate: boolean;
  outputs: string[];
}

export interface AutomationPlan {
  schema_version: string;
  action: string;
  generated_at: string;
  topic: string;
  mode: string;
  fingerprint: string;
  stages: AutomationPlanStage[];
  human_gates: Array<{ id: string; after: string; reason: string }>;
  stop_at: string;
  budget: Record<string, number | string>;
  adaptive_literature: {
    strategy: string;
    facets: Array<{ id: string; label: string; target_sources: number }>;
    coverage_plan: boolean;
  };
  run: { dataset: string | null; seeds: number; available: boolean };
  boundary: string;
}

export type InterventionKind = "engineering" | "domain";

export interface Intervention {
  id: string;
  label: string;
  kind: InterventionKind;
  note: string;
  at: string;
}

export interface EvaluationState {
  baselinePaper: number | null;
  baselineReproduced: number | null;
  hiddenAccessCount: number;
  validationSelections: number;
  evalRuleHash: string;
  audit: "pending" | "pass" | "flagged";
  trainCost: number | null;
  inferenceCost: number | null;
  interventions: Intervention[];
}

export interface EvolutionCandidate {
  id: string;
  target: string;
  patch: string;
  rationale: string;
  predicted: string;
  evidence: string;
  lease: string;
  status: "pending" | "active" | "rejected" | "rolled_back";
}

export interface EvolutionState {
  status: "idle" | "proposed" | "active" | "rejected" | "rolled_back";
  candidate: EvolutionCandidate | null;
  lease: string;
  history: Array<{ at: string; text: string }>;
}

export interface AutoStage {
  id: string;
  label: string;
  cmd: string;
  output: string;
  status: StageStatus;
  gate?: boolean;
}

export interface AutoState {
  running: boolean;
  paused: boolean;
  index: number;
  cycle: number;
  gate: "" | "claim";
  gateApproved: boolean;
}

export interface Guidance {
  id: string;
  text: string;
  at: string;
  status: "pending" | "applied";
  appliedAt?: string;
}

export interface Plugin {
  id: string;
  name: string;
  preset: "github" | "custom" | "local";
  transport: "streamable-http" | "stdio";
  url: string;
  auth: "oauth" | "env" | "none";
  readonly: boolean;
  toolsets: string[];
  status: "ready" | "disabled";
  note: string;
}

export interface ToolCall {
  id: string;
  pluginId: string;
  server: string;
  tool: string;
  args: string;
  status: "proposed" | "approved" | "denied";
  at: string;
  result?: string;
}

export interface ModelStop {
  value: string | number;
  label: string;
  detail: string;
}

export interface ModelProfile {
  id: string;
  name: string;
  short: string;
  provider: string;
  contextWindow: number;
  maxOutput: number;
  kind: "effort" | "budget" | "unsupported";
  defaultStop: string | number | null;
  stops: ModelStop[];
  note: string;
  providerId?: string;
  modelId?: string;
  apiFormat?: "openai_chat" | "openai_responses" | "anthropic_messages" | "openai_compatible";
  baseUrl?: string;
  apiKeyEnv?: string;
  inputTypes?: string[];
  capabilities?: string[];
  reasoningParam?: string;
  sourceUrl?: string;
  custom?: boolean;
}

export interface ModelSettings {
  profileId: string;
  contextLimit: number;
  maxReply: number;
  thinkingStop: string | number | null;
  compression: "off" | "auto" | "aggressive";
  threshold: number;
  keepRecent: number;
  summaryTokens: number;
}

/** 新会话默认预算（不含 profileId / thinkingStop，二者由 draftProfileId / draftThinkingStop 承担）。 */
export type ModelBudget = Pick<
  ModelSettings,
  "contextLimit" | "maxReply" | "compression" | "threshold" | "keepRecent" | "summaryTokens"
>;

export type MessageRole = "system" | "user" | "agent";

export type Card =
  | {
      type: "plan";
      queries: string[];
      scope: string;
      budget: string;
      note: string;
    }
  | {
      type: "sources";
      items: Array<{ title: string; meta: string; status: "ok" | "warn" }>;
      note: string;
    }
  | {
      type: "idea";
      gap: string;
      candidates: Array<{ id: string; text: string }>;
      note: string;
    }
  | {
      type: "protocol";
      hypothesis: string;
      baseline: string;
      metric: string;
      seeds: number;
      controls: string[];
      status: string;
    }
  | {
      type: "run";
      id: string;
      dataset: string;
      seeds: number;
      metric: string;
      mean: number;
      baseline: number;
      status: string;
      ea: string;
    }
  | {
      type: "gate";
      gate: string;
      title: string;
      reason: string;
      status: GateStatus;
    }
  | {
      type: "evolution";
      candidate: EvolutionCandidate;
    }
  | {
      type: "skill";
      skillId: string;
      name: string;
      version: string;
      status: "ok" | "needs_input" | "blocked";
      summary: string;
      steps: Array<{
        label: string;
        status: "done" | "pending" | "blocked";
        note: string;
      }>;
      note: string;
    }
  | ({ type: "review-pack" } & ReviewPackResult)
  | {
      type: "skill-use";
      skillId: string;
      name: string;
      version: string;
      reason: string;
      mode: "auto" | "explicit";
      status: "ok" | "needs_input" | "blocked";
      summary: string;
      steps: Array<{
        label: string;
        status: "done" | "pending" | "blocked";
        note: string;
      }>;
      note: string;
    }
  | {
      type: "writing";
      slots: Array<{
        id: string;
        label: string;
        status: "bound" | "pending" | "locked";
        note: string;
      }>;
      note: string;
    }
  | {
      type: "tool";
      server: string;
      tool: string;
      status: ToolCall["status"];
      args: string;
      result?: string;
    };

export interface Message {
  id: string;
  role: MessageRole;
  at: string;
  text: string;
  card?: Card;
}

export interface ResearchTask {
  id: string;
  name: string;
  goal: string;
  domain: string;
  mode: Mode;
  access: AccessMode;
  status: TaskStatus;
  workspaceId: string;
  createdAt: string;
  updatedAt: string;
  stage: number;
  completedStages: number[];
  harness: { version: string; budget: number; label: string };
  model: ModelSettings;
  usage: Record<string, TokenUsage>;
  usageDays: Record<string, Record<string, TokenUsage>>;
  guidance: Guidance[];
  plugins: string[];
  toolCalls: ToolCall[];
  budget: { used: number; total: number };
  gates: Gate[];
  coverage: Coverage;
  evidence: EvidenceItem[];
  protocol: Protocol | null;
  protocolFrozen: boolean;
  run: RunRecord | null;
  autoPlan?: AutomationPlan | null;
  evaluation: EvaluationState;
  evolution: EvolutionState;
  auto: AutoState;
  autoStages: AutoStage[];
  reviewPack?: ReviewPackResult;
  messages: Message[];
}

export interface TokenUsage {
  prompt: number;
  completion: number;
  requests: number;
}

export type ShortcutAction =
  | "commandPalette"
  | "newSession"
  | "openSettings"
  | "focusComposer"
  | "toggleContext"
  | "openSkills"
  | "openModel"
  | "openEvidence"
  | "openEval";

export type ShortcutMap = Record<ShortcutAction, string>;

export interface Preferences {
  autoExpandRunning: boolean;
  autoScroll: boolean;
  reduceMotion: boolean;
  fontScale: number;
  shortcuts: ShortcutMap;
}

export type MemoryKind = "decision" | "preference" | "constraint" | "note";

export interface MemoryEntry {
  id: string;
  text: string;
  kind: MemoryKind;
  scope: string;
  source: string;
  createdAt: string;
  syncedAt?: string;
}

export interface SettingsOrigin {
  kind: "welcome" | "task";
  taskId: string;
  label: string;
}

export interface UIState {
  contextTab: ContextTab;
  search: string;
  expandedWorkspaces: Record<string, boolean>;
  sidebarOpen: boolean;
  contextOpen: boolean;
  contextCollapsed: boolean;
  welcomeOpen: boolean;
  skillsOpen: boolean;
  draftAccess: AccessMode;
  draftProfileId: string;
  draftModelBudget: ModelBudget | null;
  modelDialogScope: "task" | "draft";
  skillDraft: SkillDraft | null;
  permissionRequest: PermissionRequest | null;
  newTaskOpen: boolean;
  newTaskMode: Mode;
  modelOpen: boolean;
  pluginsOpen: boolean;
  paletteOpen: boolean;
  settingsOpen: boolean;
  settingsSection: SettingsSection;
  settingsOrigin: SettingsOrigin;
  filesOpen: boolean;
  filesWorkspaceId: string;
  focusComposerTick: number;
}

export interface PersistedWorkspace {
  version: number;
  selectedTaskId: string;
  activeWorkspaceId: string;
  preferences: Preferences;
  workspaces: Workspace[];
  tasks: ResearchTask[];
  plugins: Plugin[];
  skills: Skill[];
  memory: MemoryEntry[];
  archivedTaskIds: string[];
}

export interface WorkspaceSnapshot extends PersistedWorkspace {
  ui: UIState;
}
