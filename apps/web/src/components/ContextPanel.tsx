import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { modelProfile } from "../domain/catalog";
import { writingCard } from "../domain/seed";
import type { AutoStage, ContextTab, EvidenceItem, GateStatus, ResearchTask } from "../domain/types";
import { selectCurrentTask, useWorkspaceStore } from "../state/workspaceStore";
import { hypothesisConvergence, literatureCoverage } from "../domain/researchBrief";
import type { ResearchCheck } from "../domain/researchBrief";
import { Icon } from "./Icon";
import { RsiStoryPanel } from "./RsiStoryPanel";

const TABS: Array<{ id: ContextTab; label: string }> = [
  { id: "run", label: "RUN" },
  { id: "evidence", label: "EVIDENCE" },
  { id: "evolution", label: "EVOLUTION" },
  { id: "eval", label: "EVAL" }
];

const GATE_NAMES: Record<string, string> = {
  Q0: "Coverage",
  G1: "Hypotheses",
  G2: "Protocol",
  S5: "EA sealed",
  G5: "Closure"
};

function statusTone(status: GateStatus): string {
  if (status === "pass") return "ok";
  if (status === "needs_human") return "warn";
  if (status === "blocked") return "bad";
  return "idle";
}

function StageAction({
  children,
  onClick,
  disabled = false,
  primary = false
}: {
  children: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      className={`stage-action${primary ? " primary" : ""}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

function CheckRail({ checks }: { checks: ResearchCheck[] }) {
  return (
    <div className="stage-checks">
      {checks.map((check) => (
        <div className={`stage-check is-${check.status}`} key={check.id}>
          <span className="stage-check-icon">
            {check.status === "ok" ? <Icon name="check" size={10} /> : check.status === "warn" ? <Icon name="alert" size={10} /> : <Icon name="lock" size={10} />}
          </span>
          <span className="stage-check-copy">
            <b>{check.label}</b>
            <small>{check.note}</small>
          </span>
          <em>{check.value}</em>
        </div>
      ))}
    </div>
  );
}

function StageDetailBody({ task, stage, index }: { task: ResearchTask; stage: AutoStage; index: number }) {
  const actions = useWorkspaceStore((state) => state.actions);
  const autoBusy = task.auto.running;
  const claim = task.evidence.find((item) => item.kind === "claim");
  const claimSigned = claim?.status === "signed";
  const hypotheses = task.evidence.filter((item) => item.kind === "hypothesis");
  const g5 = task.gates.find((gate) => gate.id === "G5");
  const coverage = literatureCoverage(task);
  const convergence = hypothesisConvergence(task);
  const writing = writingCard({ claimSigned, protocolFrozen: task.protocolFrozen });
  const slots = writing.type === "writing" ? writing.slots : [];
  const bound = slots.filter((slot) => slot.status === "bound").length;
  const pending = slots.filter((slot) => slot.status === "pending").length;
  const locked = slots.filter((slot) => slot.status === "locked").length;
  const hasStageData =
    index === 0
      ? task.coverage.sources > 0 || task.coverage.spans > 0
      : index === 1
        ? hypotheses.length > 0
        : index === 2
          ? Boolean(task.protocol)
          : index === 3
            ? Boolean(task.run)
            : index === 4
              ? Boolean(task.run || claim)
              : index === 5
                ? Boolean(task.run)
                : index === 6
                  ? Boolean(task.protocol || claim)
                  : index === 7
                    ? Boolean(g5 && g5.status !== "not_started")
                    : index === 8
                      ? Boolean(task.evolution.candidate)
                      : false;

  if (stage.status === "skipped") {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{stage.output} · skipped in manual mode；没有收集 S1/S2 证据，结论仍停在人工门。</p>
        <div className="stage-detail-actions">
          <StageAction onClick={() => actions.setMode("research")}>回到调研补证据</StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>查看证据链</StageAction>
        </div>
      </div>
    );
  }

  if (stage.status === "pending" && !hasStageData) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>尚未执行。计划输出：{stage.output}</p>
      </div>
    );
  }

  if (index === 0) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{stage.output}</p>
        <div className="stage-kv-grid">
          <span>SOURCES<b>{task.coverage.sources}</b></span>
          <span>SPANS<b>{task.coverage.spans}</b></span>
          <span>GAPS<b>{task.coverage.gaps}</b></span>
          <span>ABSTRACT-ONLY<b>{task.coverage.abstractOnly}</b></span>
        </div>
        <p className="stage-note">摘要-only 只作线索，不生成 span，也不进入 claim。</p>
        <div className="stage-brief">
          <div className="stage-brief-head">
            <span>覆盖与总结</span>
            <em>{coverage.saturation} · {Math.round(coverage.score * 100)}%</em>
          </div>
          <p>{coverage.summary}</p>
          <CheckRail checks={coverage.checks} />
          <p className="stage-note">综述/方法/评测/局限/近期等六面向由 runtime LiteratureBrief 计算；这里先审计来源、全文、span 与 gap。</p>
        </div>
        <div className="stage-detail-actions">
          <StageAction primary onClick={() => actions.setContextTab("evidence")}>查看证据链</StageAction>
          <StageAction onClick={actions.runResearch} disabled={autoBusy}>扩展检索</StageAction>
        </div>
      </div>
    );
  }

  if (index === 1) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{stage.output}</p>
        {hypotheses.length ? (
          <ul className="stage-mini-list">
            {hypotheses.map((item) => (
              <li key={item.id}>
                <b>{item.id}</b>
                <span>{item.text}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="stage-note">还没有候选假设；先完成 S1 并登记 gap。</p>
        )}
        <div className="stage-brief">
          <div className="stage-brief-head">
            <span>候选收敛</span>
            <em>{convergence.multiRef}/{convergence.candidates} multi-ref</em>
          </div>
          <p>{convergence.summary}</p>
          <CheckRail checks={convergence.checks} />
        </div>
        <div className="stage-detail-actions">
          <StageAction primary onClick={actions.designExperiment} disabled={autoBusy || hypotheses.length === 0}>
            送入实验设计
          </StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>查看证据链</StageAction>
        </div>
      </div>
    );
  }

  if (index === 2) {
    const protocol = task.protocol;
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{protocol ? stage.output : "还没有协议草案；先收敛一个候选假设并进入 S4。"}</p>
        {protocol && (
          <div className="stage-kv-grid">
            <span>BASELINE<b>{protocol.baseline}</b></span>
            <span>SEEDS<b>{protocol.seeds}</b></span>
            <span>METRIC<b>{protocol.metric}</b></span>
            <span>CONTROL<b>{protocol.controls.join(" / ")}</b></span>
          </div>
        )}
        <div className="stage-detail-actions">
          <StageAction
            primary
            onClick={actions.freezeProtocol}
            disabled={!protocol || task.protocolFrozen || autoBusy}
          >
            {task.protocolFrozen ? "协议已冻结" : "冻结协议"}
          </StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>证据链</StageAction>
        </div>
      </div>
    );
  }

  if (index === 3) {
    const run = task.run;
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{run ? stage.output : "还没有可引用的 run；先冻结协议（G2）并执行 S5a。"}</p>
        {run && (
          <div className="stage-kv-grid">
            <span>MEAN<b>{run.mean} {run.metric}</b></span>
            <span>BASELINE<b>{run.baseline}</b></span>
            <span>SEEDS<b>{run.seeds}</b></span>
            <span>EA<b>{run.ea}</b></span>
          </div>
        )}
        <div className="stage-detail-actions">
          <StageAction primary onClick={() => actions.setContextTab("evidence")}>查看 EA</StageAction>
          <StageAction
            onClick={actions.runExperiment}
            disabled={!task.protocolFrozen || autoBusy || task.evaluation.hiddenAccessCount > 0}
          >
            运行 3 seeds
          </StageAction>
        </div>
      </div>
    );
  }

  if (index === 4) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{claimSigned ? "claim 已由作者模拟签署；签名进入不可回写证据层。" : "EA 已封存，但 claim 必须由作者/PI 签核。"}</p>
        <div className="stage-kv-grid">
          <span>CLAIM<b>{claimSigned ? "SIGNED (SIM)" : claim ? "UNSIGNED" : "NOT CREATED"}</b></span>
          <span>EA<b>{task.run?.ea ?? "NOT SEALED"}</b></span>
        </div>
        <div className="stage-detail-actions">
          <StageAction primary onClick={actions.signClaim} disabled={claimSigned || !task.run}>
            {claimSigned ? "已签署" : "模拟签核"}
          </StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>查看证据链</StageAction>
        </div>
      </div>
    );
  }

  if (index === 5) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{task.run ? "SVG 与 manifest 已绑定到 EA-7c41；图不能脱离 EA 单独引用。" : "等待 EA 封存后才能绑定结果图。"}</p>
        <div className="stage-detail-actions">
          <StageAction onClick={() => actions.setContextTab("evidence")}>查看证据链</StageAction>
        </div>
      </div>
    );
  }

  if (index === 6) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{`${bound}/6 已绑定 · ${pending} pending · ${locked} locked`}</p>
        <div className="stage-kv-grid">
          <span>BOUND<b>{bound}</b></span>
          <span>LOCKED<b>{locked}</b></span>
        </div>
        <p className="stage-note">没有已签 claim 的结果/摘要槽位保持 locked；正文不先于证据填数。</p>
        <div className="stage-detail-actions">
          <StageAction primary onClick={actions.prepareWriting} disabled={autoBusy}>生成写作槽位</StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>检查证据边界</StageAction>
        </div>
      </div>
    );
  }

  if (index === 7) {
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{g5?.reason ?? "closure 尚未运行。"}</p>
        <div className="stage-detail-actions">
          <StageAction primary onClick={() => actions.setContextTab("eval")}>查看评估隔离</StageAction>
          <StageAction onClick={() => actions.setContextTab("evidence")}>证据链</StageAction>
        </div>
      </div>
    );
  }

  if (index === 8) {
    const candidate = task.evolution.candidate;
    return (
      <div className="stage-detail">
        <code>{stage.cmd}</code>
        <p>{candidate ? `${candidate.id} · ${candidate.status} · ${candidate.lease}` : "还没有自进化候选；到达 META 后生成并等待人工准入。"}</p>
        <div className="stage-detail-actions">
          <StageAction primary onClick={() => actions.setContextTab("evolution")}>查看自进化</StageAction>
        </div>
      </div>
    );
  }

  return (
    <div className="stage-detail">
      <code>{stage.cmd}</code>
      <p>{stage.output}</p>
    </div>
  );
}

function RunContext({ task }: { task: ResearchTask }) {
  const actions = useWorkspaceStore((state) => state.actions);
  const autoExpand = useWorkspaceStore((state) => state.preferences.autoExpandRunning);
  const claimSigned = task.evidence.some((item) => item.kind === "claim" && item.status === "signed");
  const done = task.autoStages.filter((stage) => stage.status === "done").length;
  const skipped = task.autoStages.filter((stage) => stage.status === "skipped").length;
  const progress = Math.round((done / task.autoStages.length) * 100);
  const pausedAtGate = task.auto.running && task.auto.paused && task.auto.gate === "claim";
  const stateLabel = !task.auto.running
    ? done === task.autoStages.length && done > 0
      ? "COMPLETE (SIM)"
      : "IDLE"
    : pausedAtGate
      ? "PAUSED AT CLAIM"
      : task.auto.paused
        ? "PAUSED"
        : "RUNNING";
  const canResume = task.auto.running && task.auto.paused && (!pausedAtGate || claimSigned);
  const activeIndex = task.auto.running
    ? task.auto.paused
      ? Math.max(task.auto.index - 1, 0)
      : task.auto.index
    : task.autoStages.findIndex((stage) => stage.status !== "done" && stage.status !== "skipped");
  const current = activeIndex >= 0 ? task.autoStages[activeIndex] : undefined;
  const [expandedStage, setExpandedStage] = useState<string | null>(null);

  useEffect(() => {
    setExpandedStage(null);
  }, [task.id]);

  useEffect(() => {
    if (!autoExpand || !task.auto.running) return;
    const stage = task.autoStages[activeIndex];
    if (stage) setExpandedStage(stage.id);
  }, [activeIndex, autoExpand, task.auto.running, task.auto.index, task.autoStages]);

  const traceLabel = !task.auto.running
    ? current
      ? `NEXT ${current.id}`
      : "COMPLETE"
    : pausedAtGate
      ? "WAITING AT GATE"
      : task.auto.paused
        ? `PAUSED AFTER ${current?.id ?? "RUN"}`
        : `RUNNING ${current?.id ?? "RUN"}`;

  return (
    <div className="context-stack">
      <section className="context-card run-overview">
        <div className="card-label">
          <span>GOVERNED AUTO</span>
          <em>{task.auto.cycle ? `CYCLE ${task.auto.cycle}` : "SIM"}</em>
        </div>
        <div className="run-state-row">
          <span className={`run-state${task.auto.running && !task.auto.paused ? " is-live" : ""}`}>
            <i />
            {stateLabel}
          </span>
          <span>
            {done}/{task.autoStages.length} stages
            {skipped > 0 ? ` · ${skipped} skipped` : ""}
          </span>
        </div>
        <div className="progress-track" aria-label={`已完成 ${progress}%`}>
          <i style={{ width: `${progress}%` }} />
        </div>
        <div className="run-numbers">
          <span>BUDGET <b>{task.budget.used}/{task.budget.total}</b></span>
          <span>HARNESS <b>{task.harness.version}</b></span>
        </div>
        {task.autoPlan && (
          <div className="auto-plan-card">
            <div className="auto-plan-head">
              <span>BACKEND PLAN</span>
              <em>{task.autoPlan.fingerprint.slice(-8)}</em>
            </div>
            <div className="auto-plan-grid">
              <span>STAGES<b>{task.autoPlan.stages.length}</b></span>
              <span>STOP<b>{task.autoPlan.stop_at}</b></span>
              <span>GATES<b>{task.autoPlan.human_gates.length}</b></span>
              <span>SOURCES<b>{String(task.autoPlan.budget.max_sources ?? "—")}</b></span>
            </div>
            <p title={task.autoPlan.boundary}>
              {task.autoPlan.adaptive_literature.strategy.replaceAll("_", " ")} · {task.autoPlan.human_gates.map((gate) => gate.id).join(" / ")}
            </p>
          </div>
        )}
        {pausedAtGate && (
          <div className="gate-hint">
            <Icon name="lock" size={13} />
            <span>{claimSigned ? "claim 已签；可以继续运行。" : "claim 未签；继续/单步会被门禁拒绝。"}</span>
          </div>
        )}
        <div className="run-controls">
          {!task.auto.running ? (
            <button type="button" className="control primary" onClick={actions.startAuto}>
              <Icon name="play" size={12} />
              启动全自动
            </button>
          ) : canResume ? (
            <button type="button" className="control primary" onClick={actions.resumeAuto}>
              <Icon name="play" size={12} />
              继续
            </button>
          ) : (
            !task.auto.paused && (
              <button type="button" className="control" onClick={actions.pauseAuto}>
                <Icon name="pause" size={12} />
                暂停
              </button>
            )
          )}
          <button
            type="button"
            className="control"
            onClick={actions.stepAuto}
            disabled={pausedAtGate && !claimSigned}
            title="执行一个阶段后暂停"
          >
            <Icon name="step" size={12} />
            单步
          </button>
          {task.auto.running && (
            <button type="button" className="control danger" onClick={actions.stopAuto}>
              <Icon name="stop" size={12} />
              停止
            </button>
          )}
        </div>
        {pausedAtGate && !claimSigned && (
          <button type="button" className="claim-sign-link" onClick={actions.signClaim}>
            模拟签署 claim，解锁人工门
            <Icon name="arrow" size={12} />
          </button>
        )}
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>STAGE TRACE</span>
          <em>{traceLabel}</em>
        </div>
        <div className="stage-list">
          {task.autoStages.map((stage, index) => {
            const isTracked = index === activeIndex;
            const isLive = isTracked && task.auto.running && !task.auto.paused;
            const isCurrent = isTracked && stage.status !== "done" && stage.status !== "skipped";
            const isDone = stage.status === "done";
            const isSkipped = stage.status === "skipped";
            const isExpanded = expandedStage === stage.id;
            return (
              <div
                className={`stage-row${isCurrent || isLive ? " is-current" : ""}${isTracked && !task.auto.running ? " is-next" : ""}${isLive ? " is-live" : ""}${isDone ? " is-done" : ""}${isSkipped ? " is-skipped" : ""}${isTracked && pausedAtGate ? " is-waiting-gate" : ""}${isExpanded ? " is-expanded" : ""}`}
                key={stage.id}
              >
                <button
                  type="button"
                  className="stage-summary"
                  onClick={() => setExpandedStage((current) => current === stage.id ? null : stage.id)}
                  aria-expanded={isExpanded}
                  aria-current={isTracked ? "step" : undefined}
                  title={isExpanded ? "收起阶段详情" : "展开阶段详情"}
                >
                  <span className="stage-status">
                    {isDone ? <Icon name="check" size={11} /> : isSkipped ? <span className="stage-skip-mark">–</span> : isCurrent ? <span className={`stage-live-dot${isLive ? " is-live" : ""}`} title={isLive ? "当前阶段 · 实时运行中" : "当前阶段 · 等待继续"} aria-label={isLive ? "当前阶段，正在运行" : "当前阶段，等待继续"} /> : <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>}
                  </span>
                  <span className="stage-name">
                    <b>{stage.id}</b>
                    <small>{stage.label}</small>
                  </span>
                  {isSkipped && <span className="stage-skip">SKIP</span>}
                  {stage.gate && <span className="stage-gate">GATE</span>}
                  <span className={`chevron${isExpanded ? " is-open" : ""}`}>
                    <Icon name="chevron" size={10} />
                  </span>
                </button>
                {isExpanded && <StageDetailBody task={task} stage={stage} index={index} />}
              </div>
            );
          })}
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>GATES</span>
          <em>{task.gates.filter((gate) => gate.status === "pass").length}/{task.gates.length} PASS</em>
        </div>
        <div className="gate-list">
          {task.gates.map((gate) => (
            <div className="gate-row" key={gate.id}>
              <span className={`gate-dot ${statusTone(gate.status)}`} />
              <span className="gate-name">
                <b>{gate.id} · {GATE_NAMES[gate.id] ?? gate.id}</b>
                <small>{gate.reason}</small>
              </span>
              <span className={`badge ${statusTone(gate.status)}`}>{gate.status.replace("_", " ")}</span>
            </div>
          ))}
          <div className="gate-row">
            <span className={`gate-dot ${claimSigned ? "ok" : task.run ? "warn" : "idle"}`} />
            <span className="gate-name">
              <b>CLAIM · human signature</b>
              <small>{claimSigned ? "已由作者模拟签署；进入不可回写证据层" : "系统不会自动生成或签署 claim"}</small>
            </span>
            <span className={`badge ${claimSigned ? "ok" : task.run ? "warn" : "idle"}`}>
              {claimSigned ? "signed" : task.run ? "unsigned" : "n/a"}
            </span>
          </div>
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>GUIDANCE QUEUE</span>
          <em>{task.guidance.filter((item) => item.status === "pending").length} PENDING</em>
        </div>
        {task.guidance.length ? (
          <div className="guidance-list">
            {[...task.guidance].reverse().slice(0, 4).map((item) => (
              <div className={`guidance-row ${item.status}`} key={item.id}>
                <span className="guidance-status">{item.status === "pending" ? "QUEUED" : "APPLIED"}</span>
                <p>{item.text}</p>
                <small>{item.status === "applied" ? `应用 ${item.appliedAt}` : `记录 ${item.at}`}</small>
              </div>
            ))}
          </div>
        ) : (
          <p className="context-empty">运行中输入任何文本都会进入指导队列，在下一阶段边界生效，并写入 trace。</p>
        )}
      </section>

      <div className="context-footnote">
        <Icon name="shield" size={12} />
        <span>静态 worker：阶段推进为本地模拟，不启动真实实验或外部调用。</span>
      </div>
    </div>
  );
}

function EvidenceContext({ task }: { task: ResearchTask }) {
  const actions = useWorkspaceStore((state) => state.actions);
  const claim = task.evidence.find((item) => item.kind === "claim");
  const closure = task.gates.find((gate) => gate.id === "G5");
  const nodes = [
    { label: "SOURCE HIT", value: `${task.coverage.sources} sources`, state: task.coverage.sources ? "ok" : "idle" },
    { label: "SPAN", value: `${task.coverage.spans} located`, state: task.coverage.spans ? "ok" : "idle" },
    { label: "CLAIM", value: claim ? (claim.status === "signed" ? "signed" : "unsigned") : "none", state: claim?.status === "signed" ? "ok" : claim ? "warn" : "idle" },
    { label: "EA", value: task.run ? task.run.ea : "not sealed", state: task.run ? "ok" : "idle" },
    { label: "CLOSURE", value: closure?.status === "pass" ? "pass" : task.run ? "locked" : "n/a", state: closure?.status === "pass" ? "ok" : task.run ? "warn" : "idle" }
  ];

  const kindLabel: Record<EvidenceItem["kind"], string> = {
    gap: "GAP",
    hypothesis: "HYPOTHESIS",
    claim: "CLAIM"
  };

  return (
    <div className="context-stack">
      <section className="context-card">
        <div className="card-label">
          <span>EVIDENCE CHAIN</span>
          <em>SPAN-ONLY</em>
        </div>
        <div className="chain">
          {nodes.map((node, index) => (
            <div className={`chain-node ${node.state}`} key={node.label}>
              <span>{node.label}</span>
              <b>{node.value}</b>
              {index < nodes.length - 1 && <i className="chain-link" />}
            </div>
          ))}
        </div>
        <div className="coverage-grid">
          <div><b>{task.coverage.spans}</b><span>SPANS</span></div>
          <div><b>{task.coverage.gaps}</b><span>GAPS</span></div>
          <div><b>{task.coverage.abstractOnly}</b><span>ABSTRACT-ONLY</span></div>
          <div><b>{claim?.status === "signed" ? 1 : 0}</b><span>SIGNED CLAIMS</span></div>
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>REGISTRY</span>
          <em>{task.evidence.length} ITEMS</em>
        </div>
        <div className="evidence-list">
          {task.evidence.length ? (
            task.evidence.map((item) => (
              <article className={`evidence-card ${item.kind}`} key={item.id}>
                <div className="evidence-head">
                  <span className="evidence-kind">{kindLabel[item.kind]}</span>
                  <span className="evidence-id">{item.id}</span>
                  <span className={`badge ${item.status === "signed" ? "ok" : item.status === "unsigned" ? "warn" : item.status === "open" ? "warn" : "idle"}`}>
                    {item.status}
                  </span>
                </div>
                <p>{item.text}</p>
                <div className="evidence-foot">
                  <span>{item.scope}</span>
                  <span>{item.refs.join(" · ")}</span>
                </div>
                {item.note && <small>{item.note}</small>}
              </article>
            ))
          ) : (
            <p className="context-empty">还没有 span 或 gap。先运行一次检索；摘要-only 来源不会进入这里。</p>
          )}
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>ADMISSION</span>
          <em>HUMAN GATES</em>
        </div>
        <div className="gate-list">
          {task.gates.map((gate) => (
            <div className="gate-row" key={gate.id}>
              <span className={`gate-dot ${statusTone(gate.status)}`} />
              <span className="gate-name"><b>{gate.id}</b><small>{gate.reason}</small></span>
              <span className={`badge ${statusTone(gate.status)}`}>{gate.status.replace("_", " ")}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="context-footnote">
        <Icon name="lock" size={12} />
        <span>claim 不进入检索层；没有全文时只保留 SourceHit 线索，不生成 span。</span>
      </div>
      <button type="button" className="context-link" onClick={() => actions.openSettings("lineage")}>
        查看沿袭与变更影响
        <Icon name="branch" size={12} />
      </button>
      <button type="button" className="context-link" onClick={() => actions.setContextTab("run")}>
        回到运行面板
        <Icon name="arrow" size={12} />
      </button>
    </div>
  );
}

function EvaluationContext({ task }: { task: ResearchTask }) {
  const actions = useWorkspaceStore((state) => state.actions);
  const evaluation = task.evaluation;
  const engineering = evaluation.interventions.filter((item) => item.kind === "engineering").length;
  const domain = evaluation.interventions.filter((item) => item.kind === "domain").length;
  const total = engineering + domain;
  const domainPercent = total ? Math.round((domain / total) * 100) : 0;
  const hiddenUsed = evaluation.hiddenAccessCount > 0;
  const auditTone = evaluation.audit === "pass" ? "ok" : evaluation.audit === "flagged" ? "bad" : "warn";
  const baselineDelta =
    evaluation.baselinePaper && evaluation.baselineReproduced
      ? ((evaluation.baselineReproduced - evaluation.baselinePaper) / evaluation.baselinePaper) * 100
      : null;
  const selectionRisk = evaluation.validationSelections > 10;

  return (
    <div className="context-stack">
      <section className="context-card eval-overview">
        <div className="card-label">
          <span>EVAL / PROTOCOL</span>
          <em>ISOLATED · SIM</em>
        </div>
        <div className="eval-stages">
          <div className="eval-stage is-done">
            <span>01</span>
            <b>Improve</b>
            <small>train / val only</small>
          </div>
          <div className={`eval-stage${hiddenUsed ? " is-done" : " is-locked"}`}>
            <span>02</span>
            <b>Evaluate</b>
            <small>held-out once</small>
          </div>
          <div className={`eval-stage${evaluation.audit !== "pending" ? " is-done" : " is-locked"}`}>
            <span>03</span>
            <b>Audit</b>
            <small>process evidence</small>
          </div>
        </div>
        <div className="eval-keyrow">
          <span>HELD-OUT ACCESS</span>
          <b className={hiddenUsed ? "is-warn" : ""}>{evaluation.hiddenAccessCount}/1</b>
        </div>
        <div className="eval-keyrow">
          <span>EVAL RULE</span>
          <b>{evaluation.evalRuleHash}</b>
        </div>
        <div className="eval-keyrow">
          <span>AUDIT</span>
          <span className={`badge ${auditTone}`}>{evaluation.audit}</span>
        </div>
        <div className="eval-actions">
          <button
            type="button"
            className="control primary"
            onClick={actions.submitEvaluation}
            disabled={!task.run || hiddenUsed || task.auto.running}
            title={!task.run ? "先完成 S5 run" : hiddenUsed ? "held-out 已消耗" : "提交一次最终评估"}
          >
            <Icon name="lock" size={12} />
            {hiddenUsed ? "已提交评估" : "提交独立评估"}
          </button>
          <button
            type="button"
            className="control"
            onClick={actions.runEvaluationAudit}
            disabled={!hiddenUsed || evaluation.audit !== "pending"}
            title={!hiddenUsed ? "先提交独立评估" : "检查验证选择与评价规则"}
          >
            <Icon name="shield" size={12} />
            {evaluation.audit === "pending" ? "运行过程审计" : "审计已完成"}
          </button>
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>REPRODUCED BASELINE</span>
          <em>NOT PAPER NUMBER</em>
        </div>
        <div className="eval-baseline">
          <div><span>PAPER</span><b>{evaluation.baselinePaper ?? "—"}</b></div>
          <div><span>REPRODUCED</span><b>{evaluation.baselineReproduced ?? "—"}</b></div>
          <div><span>Δ REPRO</span><b>{baselineDelta === null ? "—" : `${baselineDelta.toFixed(1)}%`}</b></div>
        </div>
        <p className="context-empty">改进只与复现基线比较；复现差异不隐藏，也不冒充论文原数字。</p>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>SELECTION PRESSURE</span>
          <em>{evaluation.validationSelections} VAL</em>
        </div>
        <div className={`eval-warning${selectionRisk ? " is-warn" : ""}`}>
          <Icon name={selectionRisk ? "alert" : "info"} size={12} />
          <span>
            {selectionRisk
              ? "验证选择次数偏高；审计会检查是否出现验证集过拟合。"
              : "验证选择仍在可控范围；独立测试不回流到改进阶段。"}
          </span>
        </div>
        <dl className="artifact-kv compact">
          <dt>Train cost</dt>
          <dd>{evaluation.trainCost === null ? "—" : `${evaluation.trainCost} GPU·h`}</dd>
          <dt>Inference</dt>
          <dd>{evaluation.inferenceCost === null ? "—" : `${evaluation.inferenceCost}× baseline`}</dd>
          <dt>Seeds</dt>
          <dd>{task.run?.seeds ?? "—"}</dd>
        </dl>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>METHOD MIX</span>
          <em>{domain}/{total} DOMAIN</em>
        </div>
        {total ? (
          <>
            <div className="eval-mix" title={`${domainPercent}% domain`}>
              <span style={{ width: `${domainPercent}%` }} />
            </div>
            <div className="eval-counts">
              <span><i className="is-domain" />domain {domain}</span>
              <span><i className="is-engineering" />engineering {engineering}</span>
            </div>
            <ul className="eval-interventions">
              {evaluation.interventions.slice(0, 5).map((item) => (
                <li key={item.id}>
                  <span className={`badge ${item.kind === "domain" ? "ok" : "idle"}`}>{item.kind}</span>
                  <span>
                    <b>{item.label}</b>
                    <small>{item.note}</small>
                  </span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <p className="context-empty">还没有登记干预台账；示例任务预置了工程/领域干预，新任务需在接入真实运行时后由 run diff 与实验记录写入。</p>
        )}
      </section>

      <div className="context-footnote">
        <Icon name="shield" size={12} />
        <span>独立评估与审计是控制面演示：真实系统必须由服务端隔离 held-out、冻结评价规则并保存完整轨迹。</span>
      </div>
    </div>
  );
}

function EvolutionContext({ task }: { task: ResearchTask }) {
  const actions = useWorkspaceStore((state) => state.actions);
  const candidate = task.evolution.candidate;
  const status = candidate?.status;
  const steps = [
    { label: "candidate", done: Boolean(candidate), denied: status === "rejected" },
    { label: "dry-run", done: Boolean(candidate) },
    { label: "public / hidden", done: Boolean(candidate) },
    { label: "human admit", done: status === "active" || status === "rolled_back", denied: status === "rejected" },
    { label: "lease", done: status === "active", revoked: status === "rolled_back" },
    { label: "consume / trace", done: status === "active" || status === "rolled_back" }
  ];

  return (
    <div className="context-stack">
      <RsiStoryPanel />
      <section className="context-card evolution-overview">
        <div className="card-label">
          <span>LOCAL DEMO CANDIDATE</span>
          <em>SIM</em>
        </div>
        <div className="evolution-state">
          <span className={`badge ${status === "active" ? "ok" : status === "rejected" ? "bad" : status ? "warn" : "idle"}`}>
            {task.evolution.status.toUpperCase()}
          </span>
          <span>{candidate ? candidate.id : "NO CANDIDATE"}</span>
        </div>
        <p className="evolution-copy">
          上方是真实 RSI 账本；这里是当前任务的本地演示候选。改进只在策略层提案；claim、evidence、gate、rubric、export、signature 是不可写面。准入必须经过 dry-run、public/hidden 与人工。
        </p>
        <div className="evolution-steps">
          {steps.map((step) => (
            <div className={`evolution-step${step.done ? " is-done" : ""}${step.denied ? " is-denied" : ""}${step.revoked ? " is-revoked" : ""}`} key={step.label}>
              <span>{step.done ? <Icon name="check" size={10} /> : step.denied ? <Icon name="close" size={10} /> : <i />}</span>
              {step.label}
            </div>
          ))}
        </div>
      </section>

      {candidate ? (
        <section className="context-section">
          <div className="section-title">
            <span>CANDIDATE</span>
            <em>{candidate.id}</em>
          </div>
          <article className="candidate-detail">
            <div className="candidate-target">
              <Icon name="spark" size={14} />
              <b>{candidate.target}</b>
            </div>
            <dl className="artifact-kv">
              <dt>Patch</dt>
              <dd>{candidate.patch}</dd>
              <dt>Why</dt>
              <dd>{candidate.rationale}</dd>
              <dt>Predicted</dt>
              <dd>{candidate.predicted}</dd>
              <dt>Evidence</dt>
              <dd>{candidate.evidence}</dd>
              <dt>Lease</dt>
              <dd>{candidate.lease}</dd>
            </dl>
            <div className="candidate-actions">
              {status === "pending" && (
                <>
                  <button type="button" className="action-button primary" onClick={actions.approveCandidate}>批准</button>
                  <button type="button" className="action-button danger" onClick={actions.rejectCandidate}>拒绝</button>
                </>
              )}
              {status === "active" && (
                <button type="button" className="action-button danger" onClick={actions.rollbackHarness}>撤销租约</button>
              )}
            </div>
          </article>
        </section>
      ) : (
        <section className="context-section">
          <div className="section-title">
            <span>CANDIDATE</span>
            <em>EMPTY</em>
          </div>
          <div className="context-empty-card">
            <Icon name="evolution" size={22} />
            <p>运行全自动到 META 阶段会生成一个受治理候选；也可以直接生成静态候选查看流程。</p>
            <button type="button" className="action-button" onClick={actions.previewCandidate}>
              模拟生成候选
            </button>
          </div>
        </section>
      )}

      <section className="context-section">
        <div className="section-title">
          <span>IMMUTABLE SURFACES</span>
          <em>READ-ONLY</em>
        </div>
        <div className="surface-grid">
          {["claim", "evidence", "gate", "rubric", "export", "signature"].map((surface) => (
            <span key={surface}><Icon name="lock" size={10} />{surface}</span>
          ))}
        </div>
      </section>

      <section className="context-section">
        <div className="section-title">
          <span>TRACE</span>
          <em>{task.evolution.history.length} EVENTS</em>
        </div>
        {task.evolution.history.length ? (
          <div className="history-list">
            {[...task.evolution.history].reverse().map((event, index) => (
              <div className="history-row" key={`${event.at}-${index}`}>
                <span>{event.at}</span>
                <p>{event.text}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="context-empty">暂无准入记录。候选被拒绝时负结果也会保留。</p>
        )}
      </section>

      <div className="context-footnote">
        <Icon name="shield" size={12} />
        <span>RSI 只能提案；能力增益必须绑定 public/hidden/regression 证据与人工租约。</span>
      </div>
    </div>
  );
}

export function ContextPanel() {
  const task = useWorkspaceStore(selectCurrentTask);
  const tab = useWorkspaceStore((state) => state.ui.contextTab);
  const contextOpen = useWorkspaceStore((state) => state.ui.contextOpen);
  const actions = useWorkspaceStore((state) => state.actions);
  if (!task) return null;
  const profile = modelProfile(task.model);

  return (
    <aside className={`context-panel${contextOpen ? " is-open" : ""}`} aria-label="运行上下文">
      <div className="context-head">
        <div className="context-tabs" role="tablist" aria-label="上下文视图">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={tab === item.id}
              className={tab === item.id ? "is-on" : ""}
              onClick={() => actions.setContextTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="icon-button context-collapse"
          onClick={() => actions.setUI({ contextCollapsed: true })}
          aria-label="收起运行上下文"
          title="收起运行上下文"
        >
          <Icon name="chevron" size={13} />
        </button>
        <button
          type="button"
          className="icon-button context-close"
          onClick={() => actions.setUI({ contextOpen: false })}
          aria-label="关闭运行上下文"
        >
          <Icon name="close" size={13} />
        </button>
      </div>
      <div className="context-body">
        {tab === "run" && <RunContext task={task} />}
        {tab === "evidence" && <EvidenceContext task={task} />}
        {tab === "evolution" && <EvolutionContext task={task} />}
        {tab === "eval" && <EvaluationContext task={task} />}
      </div>
      <div className="context-foot">
        <span>{profile.short} · {profile.provider}</span>
        <span>SIM · NO WORKER</span>
      </div>
    </aside>
  );
}
