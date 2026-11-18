"""二维插件契约：方法插件（怎么研究） × 任务插件（研究什么）。

MathRSI 的插件是一维的（按数学分支），因为数学的方法与领域一体。
ESE 不是：同一个"缺陷预测"可以用挖掘研究、受控实验、基准评测三种范式做，
效度威胁与报告规范完全不同。因此这里拆成两类，并允许组合。

三条硬约束：
1. 每个插件必须声明非空 cannot_support（防止过度宣称）。
2. 插件不得创建 Claim / 签署 / 改门禁。
3. 两类插件对同一威胁给出相反立场时必须报冲突，不得静默取一。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from .lifecycle import STAGES
from .models import ThreatKind


class PluginKind(Enum):
    METHOD = "method"
    TASK = "task"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]


class Advice(Enum):
    ACCEPT = "accept"
    DECLARE = "declare"
    MITIGATE = "mitigate"
    REDESIGN = "redesign"


@dataclass(frozen=True)
class ThreatStance:
    """插件对某类威胁的立场。冲突由 severity 与 advice 共同判定。"""

    kind: ThreatKind
    severity: Severity
    advice: Advice


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    kind: PluginKind
    hooks: Tuple[str, ...]
    provides: Tuple[str, ...]
    supports: Tuple[str, ...]
    cannot_support: Tuple[str, ...]
    returns_to: str
    writes: Tuple[str, ...]
    forbidden: Tuple[str, ...]
    threat_stances: Tuple[ThreatStance, ...] = ()
    failure_patterns: Tuple[str, ...] = ()

    def __post_init__(self):
        if not self.plugin_id.strip():
            raise ValueError("plugin_id 不能为空")
        if not isinstance(self.kind, PluginKind):
            raise TypeError("kind 必须是 PluginKind")

        if not self.cannot_support:
            raise ValueError(
                "插件 {0} 必须声明 cannot_support：没有边界的核验器等同于过度宣称".format(
                    self.plugin_id
                )
            )
        if any(not item.strip() for item in self.cannot_support):
            raise ValueError("cannot_support 不能含空条目")

        unknown = [hook for hook in self.hooks if hook not in STAGES]
        if unknown:
            raise ValueError(
                "插件 {0} 的 hooks 含未知阶段：{1}".format(
                    self.plugin_id, ", ".join(unknown)
                )
            )
        if self.returns_to not in STAGES:
            raise ValueError(
                "returns_to 必须是 {0} 之一".format(", ".join(STAGES))
            )

        required_forbidden = {"create_claim", "sign", "change_gate"}
        missing = required_forbidden - set(self.forbidden)
        if missing:
            raise ValueError(
                "插件 {0} 的 forbidden 必须包含：{1}".format(
                    self.plugin_id, ", ".join(sorted(missing))
                )
            )

        if self.kind is PluginKind.METHOD and len(self.threat_stances) < 3:
            raise ValueError(
                "方法插件 {0} 至少声明 3 类效度威胁立场".format(self.plugin_id)
            )
        if self.kind is PluginKind.TASK and not self.failure_patterns:
            raise ValueError(
                "任务插件 {0} 必须给出 failure_patterns".format(self.plugin_id)
            )


@dataclass(frozen=True)
class Conflict:
    threat: ThreatKind
    method_id: str
    task_id: str
    method_stance: ThreatStance
    task_stance: ThreatStance

    def explain(self) -> str:
        return (
            "{0}: 方法插件 {1} 主张 {2}/{3}，任务插件 {4} 主张 {5}/{6}".format(
                self.threat.value,
                self.method_id,
                self.method_stance.severity.value,
                self.method_stance.advice.value,
                self.task_id,
                self.task_stance.severity.value,
                self.task_stance.advice.value,
            )
        )


@dataclass(frozen=True)
class CompositeProfile:
    methods: Tuple[PluginManifest, ...]
    tasks: Tuple[PluginManifest, ...]
    hooks: Tuple[str, ...]
    supports: Tuple[str, ...]
    cannot_support: Tuple[str, ...]
    conflicts: Tuple[Conflict, ...]

    @property
    def has_blocking_conflict(self) -> bool:
        """advice 为 redesign/accept 相对立时视为阻塞；其余只提示。"""
        return any(
            {conflict.method_stance.advice, conflict.task_stance.advice}
            == {Advice.ACCEPT, Advice.REDESIGN}
            for conflict in self.conflicts
        )


def _conflicts_between(method: PluginManifest, task: PluginManifest) -> List[Conflict]:
    task_map: Dict[ThreatKind, ThreatStance] = {
        stance.kind: stance for stance in task.threat_stances
    }
    found = []
    for stance in method.threat_stances:
        other = task_map.get(stance.kind)
        if other is None:
            continue
        advice_pair = {stance.advice, other.advice}
        severity_gap = abs(stance.severity.rank - other.severity.rank)
        if advice_pair == {Advice.ACCEPT, Advice.REDESIGN} or (
            advice_pair == {Advice.ACCEPT, Advice.MITIGATE} and severity_gap >= 1
        ) or severity_gap >= 2:
            found.append(
                Conflict(
                    threat=stance.kind,
                    method_id=method.plugin_id,
                    task_id=task.plugin_id,
                    method_stance=stance,
                    task_stance=other,
                )
            )
    return found


def compose(
    methods: Tuple[PluginManifest, ...], tasks: Tuple[PluginManifest, ...]
) -> CompositeProfile:
    """组合一个方法与任务插件集合。冲突被报告而不是被吞掉。"""
    if not methods or not tasks:
        raise ValueError("至少各需要一个方法插件与任务插件")

    for method in methods:
        if method.kind is not PluginKind.METHOD:
            raise ValueError("{0} 不是方法插件".format(method.plugin_id))
    for task in tasks:
        if task.kind is not PluginKind.TASK:
            raise ValueError("{0} 不是任务插件".format(task.plugin_id))

    hook_sets = [set(method.hooks) for method in methods]
    hook_sets.extend(set(task.hooks) for task in tasks)
    hooks = tuple(stage for stage in STAGES if all(stage in s for s in hook_sets))

    supports = tuple(
        sorted({item for plugin in methods + tasks for item in plugin.supports})
    )
    cannot = tuple(
        sorted({item for plugin in methods + tasks for item in plugin.cannot_support})
    )

    conflicts = []
    for method in methods:
        for task in tasks:
            conflicts.extend(_conflicts_between(method, task))

    return CompositeProfile(
        methods=methods,
        tasks=tasks,
        hooks=hooks,
        supports=supports,
        cannot_support=cannot,
        conflicts=tuple(conflicts),
    )
