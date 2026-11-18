"""ESE 研究内核的数据模型。

设计约束（与仓库 AGENTS.md 一致）：
- 目标解释器是 Python 3.8：不使用 list[str]、dict | dict、match。
- 全部对象不可变；校验失败抛 ValueError，不静默降级。
- 三条结论轴（证据 / 复现 / 适用域）分开存放，禁止合并为单一 status。
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class EvidenceAxis(Enum):
    """证据轴：统计与证据是否支持断言原样（含效应量幅度）。"""

    SUPPORTED = "supported"
    NOT_SUPPORTED = "not_supported"
    UNDECIDABLE = "undecidable"


class ReproAxis(Enum):
    """复现轴：独立复现的结果，与证据轴正交。"""

    REPRODUCED = "reproduced"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"


class ThreatKind(Enum):
    """ACM SIGSOFT 四类效度，加可复现性作为第五类。"""

    CONSTRUCT = "construct"
    INTERNAL = "internal"
    EXTERNAL = "external"
    CONCLUSION = "conclusion"
    REPRODUCIBILITY = "reproducibility"


class ThreatStatus(Enum):
    MITIGATED = "mitigated"
    UNMITIGATED = "unmitigated"
    NOT_APPLICABLE = "not_applicable"


THREAT_QUESTIONS = {
    ThreatKind.CONSTRUCT: "指标是否真的测了所声称的构念？",
    ThreatKind.INTERNAL: "观测到的差异是否由所声称的因子导致，而非混杂？",
    ThreatKind.EXTERNAL: "结果能否推广到其他项目、语言、任务族与时间窗？",
    ThreatKind.CONCLUSION: "数据与统计是否支持该结论，功效与多重比较是否处理？",
    ThreatKind.REPRODUCIBILITY: "他人能否用同一数据、脚本与环境复现该结果？",
}

SAMPLING_KINDS = (
    "probability",
    "stratified",
    "convenience",
    "purposive",
    "census",
    "unknown",
)

SUBJECT_KINDS = ("human", "code", "llm", "mixed")


@dataclass(frozen=True)
class ValidityThreat:
    """一条效度威胁。mitigated / unmitigated 都必须写出具体内容。"""

    kind: ThreatKind
    status: ThreatStatus
    note: str

    def __post_init__(self):
        if not isinstance(self.kind, ThreatKind):
            raise TypeError("kind 必须是 ThreatKind")
        if not isinstance(self.status, ThreatStatus):
            raise TypeError("status 必须是 ThreatStatus")
        if not isinstance(self.note, str) or not self.note.strip():
            raise ValueError(
                "威胁 {0} 必须写出具体内容：缓解证据、未缓解点或不适用的理由".format(
                    self.kind.value
                )
            )


@dataclass(frozen=True)
class ClaimSpec:
    """一条可检验断言的规格。在 specified 阶段必须完整。"""

    claim_id: str
    construct: str
    operationalization: str
    population: str
    comparison: str
    metric: str
    threshold: float
    scope: str
    threats: Tuple[ValidityThreat, ...]

    def __post_init__(self):
        required_text = {
            "claim_id": self.claim_id,
            "construct": self.construct,
            "operationalization": self.operationalization,
            "population": self.population,
            "comparison": self.comparison,
            "metric": self.metric,
            "scope": self.scope,
        }
        for name, value in required_text.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{0} 不能为空".format(name))

        if len(self.scope.strip()) < 8:
            raise ValueError("scope 必须具体到 population/语言/任务族，不能只写 general")

        if not isinstance(self.threshold, (int, float)):
            raise TypeError("threshold 必须是数值")
        if not math.isfinite(float(self.threshold)):
            raise ValueError("threshold 必须是有限数值")

        seen = set()
        for threat in self.threats:
            if not isinstance(threat, ValidityThreat):
                raise TypeError("threats 只能包含 ValidityThreat")
            if threat.kind in seen:
                raise ValueError("威胁 {0} 重复".format(threat.kind.value))
            seen.add(threat.kind)

        missing = [k.value for k in ThreatKind if k not in seen]
        if missing:
            raise ValueError(
                "五类效度威胁必须齐全，缺少：{0}".format(", ".join(sorted(missing)))
            )


@dataclass(frozen=True)
class DesignFreeze:
    """设计冻结（预注册）四件套。frozen=True 才允许进入 executed。

    stopping_rule 不是可选项：没有停止规则，功效不足时就会"再跑一点"，
    直到显著为止；这正是 ESE 最常见的 p-hacking 路径。
    """

    sampling_plan: str
    power_analysis: str
    analysis_plan: str
    stopping_rule: str
    frozen: bool = False

    def __post_init__(self):
        for name in ("sampling_plan", "power_analysis", "analysis_plan", "stopping_rule"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{0} 不能为空；预注册必须在跑数之前写死".format(name))


@dataclass(frozen=True)
class DatasetCard:
    """数据集/基准卡。ESE 的知识核心之一是"这个数据集有什么坑"。"""

    name: str
    source: str
    license: str
    sampling: str
    subject_kind: str
    known_biases: Tuple[str, ...]
    time_split: Optional[str] = None
    contamination_note: str = ""

    def __post_init__(self):
        if not self.name.strip() or not self.source.strip():
            raise ValueError("name 与 source 不能为空")
        if not self.license.strip():
            raise ValueError("license 必须显式填写，未知也要写 unknown 并说明")
        if self.sampling not in SAMPLING_KINDS:
            raise ValueError(
                "sampling 必须是 {0} 之一".format(", ".join(SAMPLING_KINDS))
            )
        if self.subject_kind not in SUBJECT_KINDS:
            raise ValueError(
                "subject_kind 必须是 {0} 之一".format(", ".join(SUBJECT_KINDS))
            )
        if self.subject_kind in ("llm", "mixed") and not self.contamination_note.strip():
            raise ValueError(
                "涉及 LLM 的数据集必须填写 contamination_note："
                "发布日期、训练截止、重叠检测或私有留出集"
            )


@dataclass(frozen=True)
class FailureRecord:
    """失败图谱的一条记录。context 用有序键值对保证不可变。"""

    failure_id: str
    kind: str
    context: Tuple[Tuple[str, str], ...]
    observed: str
    diagnosis: str
    retry_condition: str
    scope: str

    def __post_init__(self):
        for name in ("failure_id", "kind", "observed", "diagnosis", "scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{0} 不能为空".format(name))
        if not self.retry_condition.strip():
            raise ValueError(
                "retry_condition 不能为空；不可重试也要写 none 并说明为什么"
            )

    def context_dict(self) -> Dict[str, str]:
        return dict(self.context)


@dataclass(frozen=True)
class ClaimState:
    """一条断言在生命周期中的当前状态。"""

    spec: ClaimSpec
    stage: str
    design: Optional[DesignFreeze] = None
    evidence: Optional[EvidenceAxis] = None
    repro: ReproAxis = ReproAxis.NOT_ATTEMPTED
    run_id: str = ""
    env_fingerprint: str = ""
    human_reason: str = ""
    invalidation_conditions: Tuple[str, ...] = ()
    repro_waived: bool = False
    repro_waiver_reason: str = ""
    residual_risk_reason: str = ""

    def __post_init__(self):
        if not isinstance(self.spec, ClaimSpec):
            raise TypeError("spec 必须是 ClaimSpec")
        if self.evidence is not None and not isinstance(self.evidence, EvidenceAxis):
            raise TypeError("evidence 必须是 EvidenceAxis")
        if not isinstance(self.repro, ReproAxis):
            raise TypeError("repro 必须是 ReproAxis")
        if self.repro_waived and not self.repro_waiver_reason.strip():
            raise ValueError("豁免复现必须写出理由")

    def can_sign(self) -> bool:
        """undecidable 可以停在 verified，但永不可签。"""
        return self.evidence in (EvidenceAxis.SUPPORTED, EvidenceAxis.NOT_SUPPORTED)

    def axes(self) -> Dict[str, str]:
        """只读投影：三轴分行，不合并。"""
        return {
            "evidence": self.evidence.value if self.evidence else "unset",
            "reproducibility": self.repro.value,
            "scope": self.spec.scope,
        }
