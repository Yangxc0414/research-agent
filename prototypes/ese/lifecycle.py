"""七段生命周期：proposed -> specified -> designed -> executed -> verified -> signed -> scoped。

两条纪律：
1. 不允许跳级；每一次推进都要满足退出条件。
2. undecidable 是合法终点，但永不可签。
"""

from dataclasses import replace
from typing import List, Optional

from .models import ClaimState, EvidenceAxis, ReproAxis, ThreatStatus

STAGES = (
    "proposed",
    "specified",
    "designed",
    "executed",
    "verified",
    "signed",
    "scoped",
)

STAGE_INDEX = {name: index for index, name in enumerate(STAGES)}


class LifecycleError(Exception):
    """非法推进或退出条件不满足。"""


def next_stage(state: ClaimState) -> Optional[str]:
    index = STAGE_INDEX.get(state.stage)
    if index is None:
        raise LifecycleError("未知阶段：{0}".format(state.stage))
    if index + 1 >= len(STAGES):
        return None
    return STAGES[index + 1]


def blockers(state: ClaimState, target: Optional[str] = None) -> List[str]:
    """返回进入 target（默认下一阶段）还缺什么。这是"当前义务"的机器可读形式。"""
    if target is None:
        target = next_stage(state)
    if target is None:
        return []

    missing = []

    if target == "specified":
        return missing

    if target == "designed":
        if state.design is None:
            missing.append("design（抽样计划 / 功效分析 / 分析计划 / 停止规则）")
        elif not state.design.frozen:
            missing.append("design.frozen=True（设计尚未冻结）")
        return missing

    if target == "executed":
        if not state.run_id.strip():
            missing.append("run_id")
        if not state.env_fingerprint.strip():
            missing.append("env_fingerprint（环境与依赖指纹）")
        return missing

    if target == "verified":
        if state.evidence is None:
            missing.append("evidence（证据轴未定）")
        if state.repro is ReproAxis.NOT_ATTEMPTED and not state.repro_waived:
            missing.append(
                "repro（复现轴为 not_attempted；要么复现，要么显式豁免并写理由）"
            )
        return missing

    if target == "signed":
        if not state.can_sign():
            missing.append(
                "证据轴为 undecidable：不可签署；应停在 verified 补功效或改写断言"
            )
        unmitigated = [
            threat.kind.value
            for threat in state.spec.threats
            if threat.status is ThreatStatus.UNMITIGATED
        ]
        if unmitigated and not state.residual_risk_reason.strip():
            missing.append(
                "residual_risk_reason（未缓解威胁：{0}；必须写明残余风险与适用范围）".format(
                    ", ".join(unmitigated)
                )
            )
        if not state.human_reason.strip():
            missing.append("human_reason（人签理由）")
        return missing

    if target == "scoped":
        if not state.invalidation_conditions:
            missing.append("invalidation_conditions（结论在什么条件下失效）")
        return missing

    return missing


def advance(state: ClaimState, target: Optional[str] = None, **changes) -> ClaimState:
    """推进一个阶段。跳级或条件不满足时抛 LifecycleError。"""
    expected = next_stage(state)
    if expected is None:
        raise LifecycleError("已处于最终阶段 {0}".format(state.stage))

    if target is None:
        target = expected
    if target != expected:
        raise LifecycleError(
            "不允许跳级：当前 {0}，下一步只能是 {1}，请求的是 {2}".format(
                state.stage, expected, target
            )
        )

    candidate = replace(state, stage=target, **changes)
    missing = blockers(candidate, target)
    if missing:
        raise LifecycleError(
            "进入 {0} 缺少：{1}".format(target, "; ".join(missing))
        )
    return candidate


def describe(state: ClaimState) -> str:
    """一行可读状态，供日志与测试断言。"""
    evidence = state.evidence.value if state.evidence else "unset"
    return "{0} | evidence={1} | repro={2} | scope={3}".format(
        state.stage, evidence, state.repro.value, state.spec.scope
    )
