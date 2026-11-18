"""框架元演化的准入闸：从 durable 失败到可回滚的版本变化。

这不是"让 Agent 改自己"的开关。它只回答一个窄问题：一条由真实研究证据
提出的框架改动，是否值得进入下一版？规则刻意保守：

- 候选不得触碰 claim / evidence / gate / rubric / signature / export / heldout；
- 候选必须有 durable 失败作为来源；
- 候选必须在至少两个 held-out 任务上不退化，且至少有一个正向证据；
- 候选必须有人写理由；没有理由只能 defer，不能 adopt；
- 成本明显上升时拒绝，除非人明确接受；
- 只支持一层改动：base / method plugin / task plugin / dataset card / workspace。

这些规则是原型，不是生产门禁；它们演示"元演化必须比研究循环更慢"。
"""

import math
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

LAYERS = ("base", "method_plugin", "task_plugin", "dataset_card", "workspace")
FORBIDDEN_TOKENS = (
    "claim",
    "evidence",
    "gate",
    "rubric",
    "signature",
    "export",
    "heldout",
    "held-out",
)


@dataclass(frozen=True)
class EvolutionCandidate:
    candidate_id: str
    layer: str
    target: str
    change: str
    rationale: str
    source_failures: Tuple[str, ...]
    predicted_effect: str
    touches: Tuple[str, ...] = ()
    human_reason: str = ""

    def __post_init__(self):
        for name in ("candidate_id", "target", "change", "rationale", "predicted_effect"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{0} 不能为空".format(name))
        if self.layer not in LAYERS:
            raise ValueError(
                "layer 必须是 {0} 之一".format(", ".join(LAYERS))
            )
        if not self.source_failures:
            raise ValueError(
                "候选必须引用至少一条 durable 失败：没有失败来源的改动只是偏好"
            )
        for failure_id in self.source_failures:
            if not isinstance(failure_id, str) or not failure_id.strip():
                raise ValueError("source_failures 不能含空条目")

    def forbidden_hits(self) -> Tuple[str, ...]:
        # 只看"改什么"，不看"为什么改"：rationale 里出现 evidence 是正常的，
        # 不能因此把候选判成触碰不可变面。
        haystack = " ".join(
            [self.target, self.change] + [str(item) for item in self.touches]
        ).lower()
        hits = []
        for token in FORBIDDEN_TOKENS:
            if token in haystack:
                hits.append(token)
        return tuple(sorted(set(hits)))


@dataclass(frozen=True)
class ShadowTask:
    task_id: str
    public_delta: float
    hidden_delta: Optional[float]
    n: int
    cost_delta: float = 0.0

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("task_id 不能为空")
        for name in ("public_delta", "cost_delta"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError("{0} 必须是有限数值".format(name))
        if self.hidden_delta is not None and not math.isfinite(float(self.hidden_delta)):
            raise ValueError("hidden_delta 必须是有限数值或 None")
        if not isinstance(self.n, int) or self.n < 1:
            raise ValueError("n 必须是正整数")


@dataclass(frozen=True)
class EvolutionDecision:
    status: str
    reasons: Tuple[str, ...]


def _mean(values: Sequence[float]) -> float:
    return sum(values) / float(len(values))


def evaluate_candidate(
    candidate: EvolutionCandidate,
    tasks: Sequence[ShadowTask],
    *,
    durable_failure_ids: Optional[Iterable[str]] = None,
    min_hidden_tasks: int = 2,
    max_cost_delta: float = 0.20,
) -> EvolutionDecision:
    """返回 adopt / reject / defer。adopt 仍需人执行，不由函数自动生效。"""
    reasons = []

    hits = candidate.forbidden_hits()
    if hits:
        return EvolutionDecision(
            status="reject",
            reasons=(
                "候选触碰不可变面：{0}；claim/evidence/gate/rubric/signature/"
                "export/heldout 不属于可演化对象".format(", ".join(hits)),
            ),
        )

    if durable_failure_ids is not None:
        allowed = set(str(item) for item in durable_failure_ids)
        unknown = [item for item in candidate.source_failures if item not in allowed]
        if unknown:
            return EvolutionDecision(
                status="reject",
                reasons=(
                    "候选引用了非 durable/未知失败：{0}；"
                    "operational 失败不得驱动框架演化".format(", ".join(unknown)),
                ),
            )

    if not tasks:
        return EvolutionDecision(
            status="reject",
            reasons=("没有 shadow 任务：不能只凭一个失败故事改框架",),
        )

    hidden = [task for task in tasks if task.hidden_delta is not None]
    if len(hidden) < min_hidden_tasks:
        return EvolutionDecision(
            status="defer",
            reasons=(
                "held-out 任务只有 {0} 个，至少需要 {1} 个；public 提升不足以采纳".format(
                    len(hidden), min_hidden_tasks
                ),
            ),
        )

    mean_public = _mean([task.public_delta for task in tasks])
    if mean_public <= 0:
        return EvolutionDecision(
            status="reject",
            reasons=("public 平均变化 {0:+.3f} 不为正：候选连公开任务都没改善".format(mean_public),),
        )

    mean_hidden = _mean([float(task.hidden_delta) for task in hidden])
    if mean_hidden <= 0:
        return EvolutionDecision(
            status="reject",
            reasons=("held-out 平均变化 {0:+.3f} 不为正：公开提升没有迁移".format(mean_hidden),),
        )

    regressions = [
        task for task in hidden if float(task.hidden_delta) < 0.0
    ]
    if regressions:
        return EvolutionDecision(
            status="reject",
            reasons=tuple(
                "held-out 任务 {0} 退化 {1:+.3f}；不接受以平均分掩盖回归".format(
                    task.task_id, float(task.hidden_delta)
                )
                for task in regressions
            ),
        )

    mean_cost = _mean([task.cost_delta for task in tasks])
    if mean_cost > max_cost_delta:
        if not candidate.human_reason.strip():
            return EvolutionDecision(
                status="reject",
                reasons=(
                    "平均成本上升 {0:+.3f} 超过阈值 {1:.2f}，且没有人接受该代价".format(
                        mean_cost, max_cost_delta
                    ),
                ),
            )
        reasons.append(
            "人接受成本上升 {0:+.3f}（阈值 {1:.2f}）".format(
                mean_cost, max_cost_delta
            )
        )

    if not candidate.human_reason.strip():
        return EvolutionDecision(
            status="defer",
            reasons=tuple(
                reasons
                + ["缺少 human_reason：候选可以提议，不能自己采纳",]
            ),
        )

    return EvolutionDecision(
        status="adopt",
        reasons=tuple(
            reasons
            + [
                "public 平均 {0:+.3f}；held-out 平均 {1:+.3f}；"
                "回归 0；成本 {2:+.3f}".format(mean_public, mean_hidden, mean_cost),
                "采纳是人的动作；本函数只给出准入建议",
            ]
        ),
    )


@dataclass(frozen=True)
class EvolutionRecord:
    version: str
    candidate_id: str
    status: str
    evidence: Tuple[str, ...]
    rollback_to: str


def record_decision(
    version: str,
    candidate: EvolutionCandidate,
    decision: EvolutionDecision,
    *,
    rollback_to: str,
) -> EvolutionRecord:
    if not version.strip() or not rollback_to.strip():
        raise ValueError("version 与 rollback_to 不能为空")
    if decision.status not in ("adopt", "reject", "defer"):
        raise ValueError("未知决策状态")
    return EvolutionRecord(
        version=version,
        candidate_id=candidate.candidate_id,
        status=decision.status,
        evidence=decision.reasons,
        rollback_to=rollback_to,
    )
