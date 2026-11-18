"""最难关口探针、三轴判定与失败图谱建议。

MathRSI 的 v6 用"最难余域预检"防止易分支通过掩盖难核心；ESE 的对应物不是
"最难引理"，而是"最可能杀死这条断言的那个效度威胁"。本模块把该判断做成
可测试的纯函数：

1. 设计前必须先跑至少一个威胁探针；失败时返回设计/规格，而不是继续跑大实验。
2. 三轴判定不得压成一个 signable 布尔；undecidable 永不可签。
3. 失败图谱只回答 durable 失败；operational 失败只进运行日志。
"""

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from .failure_taxonomy import to_memory
from .models import ClaimState, EvidenceAxis, FailureRecord, ReproAxis, ThreatKind

PROBE_RESULTS = ("passed", "failed", "inconclusive")


@dataclass(frozen=True)
class ThreatProbe:
    """一条有界的效度威胁探针。

    probe 不是"再跑一次主实验"：它必须比主实验便宜，并且其结果能改变下一步。
    """

    probe_id: str
    threat: ThreatKind
    question: str
    cheapest_test: str
    result: str
    evidence: str
    cost: str = "bounded"

    def __post_init__(self):
        for name in ("probe_id", "question", "cheapest_test", "evidence", "cost"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{0} 不能为空".format(name))
        if not isinstance(self.threat, ThreatKind):
            raise TypeError("threat 必须是 ThreatKind")
        if self.result not in PROBE_RESULTS:
            raise ValueError(
                "result 必须是 {0} 之一".format(", ".join(PROBE_RESULTS))
            )

    def return_stage(self) -> str:
        """失败时回到哪一段：构念问题回规格，其余回设计。"""
        if self.result == "passed":
            return "designed"
        if self.threat is ThreatKind.CONSTRUCT:
            return "specified"
        return "designed"

    def action(self) -> str:
        if self.result == "passed":
            return "continue"
        if self.result == "failed":
            return "respecify" if self.threat is ThreatKind.CONSTRUCT else "redesign"
        return "stop"


@dataclass(frozen=True)
class ProbeGate:
    allowed: bool
    action: str
    return_to: str
    reasons: Tuple[str, ...]


def gate_probes(probes: Sequence[ThreatProbe]) -> ProbeGate:
    """设计冻结前的最难关口门。

    规则（fail-closed）：
    - 没有探针 => 不允许进入 designed；
    - 任一探针 failed => 不允许，回到对应阶段；
    - 任一探针 inconclusive => 不允许，停止扩批；
    - 全部 passed => 允许。
    """
    if not probes:
        return ProbeGate(
            allowed=False,
            action="stop",
            return_to="specified",
            reasons=("没有威胁探针：先证明这条断言最可能怎么死，再谈大实验",),
        )

    failed = [probe for probe in probes if probe.result == "failed"]
    if failed:
        first = failed[0]
        return ProbeGate(
            allowed=False,
            action=first.action(),
            return_to=first.return_stage(),
            reasons=tuple(
                "{0}（{1}）失败：{2}".format(
                    probe.probe_id, probe.threat.value, probe.evidence
                )
                for probe in failed
            ),
        )

    inconclusive = [probe for probe in probes if probe.result == "inconclusive"]
    if inconclusive:
        return ProbeGate(
            allowed=False,
            action="stop",
            return_to="designed",
            reasons=tuple(
                "{0}（{1}）不可判定：{2}".format(
                    probe.probe_id, probe.threat.value, probe.evidence
                )
                for probe in inconclusive
            ),
        )

    return ProbeGate(
        allowed=True,
        action="continue",
        return_to="designed",
        reasons=("全部威胁探针通过；仍需在协议中写出探针覆盖范围",),
    )


@dataclass(frozen=True)
class StudyDecision:
    status: str
    signable: bool
    reasons: Tuple[str, ...]
    next_action: str


def decide(state: ClaimState) -> StudyDecision:
    """从三轴状态派生下一步；不产生 Claim，只说明还缺什么。"""
    if state.stage in ("proposed", "specified", "designed", "executed"):
        return StudyDecision(
            status="not_ready",
            signable=False,
            reasons=("当前阶段 {0} 尚未进入 verified".format(state.stage),),
            next_action="按阶段退出条件推进",
        )

    if state.evidence is None:
        return StudyDecision(
            status="undecidable",
            signable=False,
            reasons=("证据轴未定：没有区间/效应量就不能读方向",),
            next_action="执行分析或补功效；不要先写结论",
        )

    if state.evidence is EvidenceAxis.UNDECIDABLE:
        return StudyDecision(
            status="undecidable",
            signable=False,
            reasons=(
                "证据轴为 undecidable：区间跨零或功效不足；"
                "不得用点估计冒充方向",
            ),
            next_action="加种子/收窄主张/换设计；不要重跑到显著",
        )

    if state.repro is ReproAxis.NOT_ATTEMPTED and not state.repro_waived:
        return StudyDecision(
            status="pending_replication",
            signable=False,
            reasons=("复现轴为 not_attempted；要么独立复现，要么显式豁免",),
            next_action="独立复现或写明豁免理由",
        )

    if not state.can_sign():
        return StudyDecision(
            status="blocked",
            signable=False,
            reasons=("当前三轴组合不可签署",),
            next_action="回到设计或补证据",
        )

    return StudyDecision(
        status="signable",
        signable=True,
        reasons=("证据轴已定且复现轴不是 not_attempted",),
        next_action="人签前核对适用域、失效条件与断言数值边界",
    )


@dataclass(frozen=True)
class FailureAdvice:
    failure_id: str
    kind: str
    diagnosis: str
    retry_condition: str
    scope: str
    applicability: str


def _matches(record: FailureRecord, keywords: Sequence[str]) -> bool:
    haystack = " ".join(
        [record.observed, record.diagnosis, record.scope, record.retry_condition]
        + [value for _, value in record.context]
    ).lower()
    return any(str(keyword).lower() in haystack for keyword in keywords if keyword)


def advise_failures(
    failures: Iterable[FailureRecord],
    *,
    keywords: Sequence[str] = (),
    limit: int = 5,
) -> List[FailureAdvice]:
    """只从 durable 失败里取建议；operational 失败永远不进入图谱建议。"""
    out: List[FailureAdvice] = []
    for record in failures:
        admitted = to_memory(record)
        if admitted is None:
            continue
        if keywords and not _matches(admitted, keywords):
            continue
        out.append(
            FailureAdvice(
                failure_id=record.failure_id,
                kind=record.kind,
                diagnosis=record.diagnosis,
                retry_condition=record.retry_condition,
                scope=record.scope,
                applicability="scope/keyword 命中；复用前仍需核对当前参数",
            )
        )
        if len(out) >= limit:
            break
    return out
