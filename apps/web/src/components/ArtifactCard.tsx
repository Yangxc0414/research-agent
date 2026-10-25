import type { ReactNode } from "react";
import type { Card } from "../domain/types";
import { selectCurrentTask, useWorkspaceStore } from "../state/workspaceStore";
import { Icon } from "./Icon";

function CardHead({ label, meta }: { label: string; meta?: string }) {
  return (
    <div className="artifact-head">
      <span>{label}</span>
      {meta && <em>{meta}</em>}
    </div>
  );
}

function Actions({ children }: { children: ReactNode }) {
  return <div className="artifact-actions">{children}</div>;
}

function ActionButton({
  children,
  onClick,
  variant = "quiet",
  disabled = false
}: {
  children: ReactNode;
  onClick: () => void;
  variant?: "primary" | "quiet" | "danger";
  disabled?: boolean;
}) {
  return (
    <button type="button" className={`action-button ${variant}`} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function ArtifactCard({ card }: { card: Card }) {
  const task = useWorkspaceStore(selectCurrentTask);
  const actions = useWorkspaceStore((state) => state.actions);
  const autoBusy = Boolean(task?.auto.running);
  const evaluated = (task?.evaluation.hiddenAccessCount ?? 0) > 0;

  if (card.type === "plan") {
    return (
      <article className="artifact">
        <CardHead label="PLAN / RETRIEVAL" meta="span-only" />
        <ol className="query-list">
          {card.queries.map((query, index) => (
            <li key={query}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              {query}
            </li>
          ))}
        </ol>
        <dl className="artifact-kv">
          <dt>范围</dt>
          <dd>{card.scope}</dd>
          <dt>预算</dt>
          <dd>{card.budget}</dd>
        </dl>
        <p className="artifact-note">{card.note}</p>
        <Actions>
          <ActionButton variant="primary" onClick={actions.runResearch} disabled={autoBusy}>
            开始检索
          </ActionButton>
          <ActionButton onClick={actions.focusComposer}>调整问题</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "sources") {
    return (
      <article className="artifact">
        <CardHead label="COVERAGE / SOURCES" meta={`${card.items.length} sources`} />
        <ul className="source-list">
          {card.items.map((item, index) => (
            <li key={item.title}>
              <span className="source-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="source-copy">
                <b>{item.title}</b>
                <small>{item.meta}</small>
              </span>
              <span className={`badge ${item.status === "ok" ? "ok" : "warn"}`}>
                {item.status === "ok" ? "FULL" : "ABSTRACT"}
              </span>
            </li>
          ))}
        </ul>
        <p className="artifact-note">{card.note}</p>
        <Actions>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>查看 gap</ActionButton>
          <ActionButton onClick={actions.runResearch} disabled={autoBusy}>扩展检索</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "idea") {
    return (
      <article className="artifact">
        <CardHead label="GAP → HYPOTHESES" meta="S2–S3" />
        <div className="gap-block">
          <span>OPEN GAP</span>
          <p>{card.gap}</p>
        </div>
        <ul className="candidate-list">
          {card.candidates.map((candidate) => (
            <li key={candidate.id}>
              <span className="candidate-id">{candidate.id}</span>
              <span>{candidate.text}</span>
            </li>
          ))}
        </ul>
        <p className="artifact-note">{card.note}</p>
        <Actions>
          <ActionButton variant="primary" onClick={actions.designExperiment} disabled={autoBusy}>
            送入实验设计
          </ActionButton>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>查看证据链</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "protocol") {
    const frozen = task?.protocolFrozen ?? false;
    return (
      <article className="artifact">
        <CardHead label="PROTOCOL / S4" meta={frozen ? "FROZEN" : "DRAFT"} />
        <p className="artifact-lede">{card.hypothesis}</p>
        <dl className="artifact-kv">
          <dt>Baseline</dt>
          <dd>{card.baseline}</dd>
          <dt>主指标</dt>
          <dd>{card.metric}</dd>
          <dt>Seeds</dt>
          <dd>{card.seeds}</dd>
          <dt>对照</dt>
          <dd>{card.controls.join(" · ")}</dd>
        </dl>
        <div className="artifact-status-row">
          <span className={`badge ${frozen ? "ok" : "warn"}`}>
            {frozen ? "G2 PASS (SIM)" : "G2 NEEDS_HUMAN"}
          </span>
          <span>冻结后不得改写主指标、对照与 seeds</span>
        </div>
        <Actions>
          <ActionButton variant="primary" onClick={actions.freezeProtocol} disabled={frozen || autoBusy}>
            {frozen ? "协议已冻结" : "冻结协议"}
          </ActionButton>
          <ActionButton onClick={actions.runExperiment} disabled={!frozen || autoBusy || evaluated}>运行 3 seeds</ActionButton>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>证据链</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "run") {
    const signed = task?.evidence.some((item) => item.kind === "claim" && item.status === "signed") ?? false;
    const delta = card.mean - card.baseline;
    return (
      <article className="artifact">
        <CardHead label={`RUN / ${card.id}`} meta="EA SEALED" />
        <div className="metric-grid">
          <div>
            <span>MEAN T80</span>
            <b>{card.mean}<small> h</small></b>
          </div>
          <div>
            <span>BASELINE</span>
            <b>{card.baseline}<small> h</small></b>
          </div>
          <div className="metric-delta">
            <span>DELTA</span>
            <b>+{delta}<small> h</small></b>
          </div>
        </div>
        <dl className="artifact-kv compact">
          <dt>Dataset</dt>
          <dd>{card.dataset}</dd>
          <dt>Seeds</dt>
          <dd>{card.seeds}</dd>
          <dt>EA</dt>
          <dd>{card.ea}</dd>
          <dt>Claim</dt>
          <dd>{signed ? "SIGNED (SIM)" : "UNSIGNED · 停在人工门"}</dd>
        </dl>
        <p className="artifact-note">数值来自本地 fixture，仅用于演示 EA → claim 的边界，不作为真实材料实验结论。</p>
        <Actions>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>查看 EA</ActionButton>
          <ActionButton variant="primary" onClick={actions.signClaim} disabled={signed}>
            {signed ? "claim 已签" : "模拟签核 claim"}
          </ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "gate") {
    const signed = task?.evidence.some((item) => item.kind === "claim" && item.status === "signed") ?? false;
    const passed = signed || card.status === "pass";
    return (
      <article className={`artifact gate-card${passed ? " is-pass" : ""}`}>
        <CardHead label={card.gate} meta={passed ? "SIGNED (SIM)" : "HUMAN GATE"} />
        <div className="gate-title">
          <span className="gate-icon">
            <Icon name={passed ? "check" : "lock"} size={16} />
          </span>
          <div>
            <b>{passed ? "claim 已由作者模拟签署" : card.title}</b>
            <p>{card.reason}</p>
          </div>
        </div>
        <Actions>
          <ActionButton variant={passed ? "quiet" : "primary"} onClick={actions.signClaim} disabled={passed}>
            {passed ? "已签署" : "模拟签核"}
          </ActionButton>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>查看证据链</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "evolution") {
    const candidate =
      task?.evolution.candidate?.id === card.candidate.id ? task.evolution.candidate : card.candidate;
    const status = candidate.status;
    return (
      <article className="artifact evolution-card">
        <CardHead label={`EVOLUTION / ${candidate.id}`} meta={status.toUpperCase()} />
        <div className="evolution-target">
          <span>TARGET</span>
          <b>{candidate.target}</b>
          <span className={`badge ${status === "active" ? "ok" : status === "rejected" ? "bad" : "warn"}`}>
            {status}
          </span>
        </div>
        <dl className="artifact-kv">
          <dt>Patch</dt>
          <dd>{candidate.patch}</dd>
          <dt>Rationale</dt>
          <dd>{candidate.rationale}</dd>
          <dt>Predicted</dt>
          <dd>{candidate.predicted}</dd>
          <dt>Evidence</dt>
          <dd>{candidate.evidence}</dd>
          <dt>Lease</dt>
          <dd>{candidate.lease}</dd>
        </dl>
        <p className="artifact-note">不可写层：claim / evidence / gate / rubric / export / signature。候选只能改策略参数。</p>
        <Actions>
          {status === "pending" && (
            <>
              <ActionButton variant="primary" onClick={actions.approveCandidate}>
                批准候选
              </ActionButton>
              <ActionButton variant="danger" onClick={actions.rejectCandidate}>
                拒绝并保留负结果
              </ActionButton>
            </>
          )}
          {status === "active" && (
            <ActionButton variant="danger" onClick={actions.rollbackHarness}>
              撤销租约并回滚
            </ActionButton>
          )}
          <ActionButton onClick={() => actions.setContextTab("evolution")}>查看自进化</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "skill-use") {
    return (
      <article className="artifact skill-use-card">
        <div className="skill-use-head">
          <span className="skill-use-mark"><Icon name="spark" size={13} /></span>
          <div className="skill-use-copy">
            <span className="skill-use-kicker">
              SKILL / {card.mode === "auto" ? "按需加载" : "手动加载"}
            </span>
            <b>{card.name}</b>
            <small>{card.reason}</small>
          </div>
          <span className="skill-use-version">v{card.version}</span>
        </div>
        <p className="skill-use-summary">{card.summary}</p>
        {card.steps.length > 0 && (
          <ul className="skill-use-steps">
            {card.steps.map((step) => (
              <li key={step.label} data-status={step.status}>
                <span className="skill-use-dot">
                  {step.status === "done" ? <Icon name="check" size={9} /> : step.status === "blocked" ? <Icon name="lock" size={9} /> : <i />}
                </span>
                <span className="skill-use-step-copy">
                  <b>{step.label}</b>
                  <small>{step.note}</small>
                </span>
              </li>
            ))}
          </ul>
        )}
        <p className="skill-use-note">{card.note}</p>
        <Actions>
          <ActionButton onClick={() => actions.openOverlay("skillsOpen")}>查看 Skill</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "skill") {
    return (
      <article className="artifact skill-card">
        <CardHead label={`SKILL / ${card.skillId}`} meta={`v${card.version} · ${card.status}`} />
        <div className="skill-summary">
          <span className="skill-mark"><Icon name="spark" size={13} /></span>
          <p>{card.summary}</p>
        </div>
        <ul className="skill-steps">
          {card.steps.map((step) => (
            <li key={step.label} data-status={step.status}>
              <span className="skill-step-dot">
                {step.status === "done" ? <Icon name="check" size={10} /> : step.status === "blocked" ? <Icon name="lock" size={10} /> : <i />}
              </span>
              <span className="skill-step-copy">
                <b>{step.label}</b>
                <small>{step.note}</small>
              </span>
              <span className="skill-step-state">{step.status.toUpperCase()}</span>
            </li>
          ))}
        </ul>
        <p className="artifact-note">{card.note}</p>
        <Actions>
          <ActionButton variant="primary" onClick={() => actions.invokeSkill(card.skillId)} disabled={autoBusy}>
            重新调用
          </ActionButton>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>查看证据链</ActionButton>
        </Actions>
      </article>
    );
  }

  if (card.type === "writing") {
    const bound = card.slots.filter((slot) => slot.status === "bound").length;
    const locked = card.slots.filter((slot) => slot.status === "locked").length;
    return (
      <article className="artifact writing-card">
        <CardHead label="WRITING / SLOT BINDING" meta={`${bound}/${card.slots.length} bound`} />
        <ul className="writing-slots">
          {card.slots.map((slot) => (
            <li key={slot.id} data-status={slot.status}>
              <span className="slot-id">{slot.id}</span>
              <span className="slot-copy">
                <b>{slot.label}</b>
                <small>{slot.note}</small>
              </span>
              <span className={`slot-badge ${slot.status}`}>
                {slot.status === "bound" ? "BOUND" : slot.status === "pending" ? "PENDING" : "LOCKED"}
              </span>
            </li>
          ))}
        </ul>
        <p className="artifact-note">{card.note}</p>
        <Actions>
          <ActionButton variant="primary" onClick={actions.prepareWriting} disabled={autoBusy}>
            刷新槽位绑定
          </ActionButton>
          <ActionButton onClick={() => actions.setContextTab("evidence")}>检查证据边界</ActionButton>
          {locked > 0 && <span className="writing-lock-note">{locked} 个槽位等待已签 claim</span>}
        </Actions>
      </article>
    );
  }

  const liveCall = task?.toolCalls.find((call) => call.tool === card.tool && call.args === card.args);
  const status = liveCall?.status ?? card.status;
  return (
    <article className="artifact tool-card">
      <CardHead label="TOOL CALL / MCP" meta={status.toUpperCase()} />
      <div className="tool-head">
        <span className="tool-server">
          <Icon name="terminal" size={14} />
          {card.server}
        </span>
        <code>{card.tool}</code>
      </div>
      <dl className="artifact-kv compact">
        <dt>Arguments</dt>
        <dd>{card.args}</dd>
        <dt>Security</dt>
        <dd>read-only · 结果视为 UNTRUSTED</dd>
        {liveCall?.result && (
          <>
            <dt>Result</dt>
            <dd>{liveCall.result}</dd>
          </>
        )}
      </dl>
      <Actions>
        {status === "proposed" && (
          <ActionButton variant="primary" onClick={() => actions.openOverlay("pluginsOpen")}>
            处理审批
          </ActionButton>
        )}
        {status !== "proposed" && <span className="tool-outcome">状态：{status}</span>}
      </Actions>
    </article>
  );
}
