"""失败分类学与记忆准入。

MathRSI 的 anti-self-poisoning 只处理"环境失败 / 瞬时错误"，ESE 的环境噪声多得多。
这里把失败分成两类，只有 durable 允许进入失败图谱：

    operational（只进运行日志）：environment / data_unavailable / transient / rate_limit
    durable（进图谱，可跨任务复用）：design_flaw / construct_mismatch /
                                      underpowered / contamination / leakage /
                                      population_drift / true_null

未知类型 fail-closed：既不当作 durable，也不静默丢弃。leakage 与 contamination
分开，是因为修法不同：前者是时间/重复/特征泄漏，后者是训练语料与基准重叠。
"""

from typing import Dict, List, Optional

from .models import FailureRecord

DURABLE_KINDS = frozenset(
    (
        "design_flaw",
        "construct_mismatch",
        "underpowered",
        "contamination",
        "leakage",
        "population_drift",
        "true_null",
    )
)

OPERATIONAL_KINDS = frozenset(
    (
        "environment",
        "data_unavailable",
        "transient",
        "rate_limit",
    )
)

# 最容易被误写的几类，强制带出可复核的上下文。
REQUIRED_CONTEXT = {
    "underpowered": ("n",),
    "contamination": ("dataset", "overlap_check"),
    "leakage": ("dataset", "overlap_check"),
    "population_drift": ("population", "time_window"),
    "construct_mismatch": ("construct", "operationalization"),
}


class FailureKindError(ValueError):
    """未知失败类型。"""


def classify(kind: str) -> str:
    """返回 durable / operational。未知类型直接拒绝。"""
    if kind in DURABLE_KINDS:
        return "durable"
    if kind in OPERATIONAL_KINDS:
        return "operational"
    raise FailureKindError(
        "未知失败类型 {0!r}；允许值：{1}".format(
            kind, ", ".join(sorted(DURABLE_KINDS | OPERATIONAL_KINDS))
        )
    )


def admits_to_atlas(record: FailureRecord) -> bool:
    """只有 durable 才进失败图谱。"""
    return classify(record.kind) == "durable"


def _check_context(record: FailureRecord) -> None:
    required = REQUIRED_CONTEXT.get(record.kind, ())
    present = record.context_dict()
    missing = [key for key in required if not present.get(key, "").strip()]
    if missing:
        raise ValueError(
            "失败 {0}（{1}）缺少可复核上下文：{2}".format(
                record.failure_id, record.kind, ", ".join(missing)
            )
        )


def to_memory(record: FailureRecord) -> Optional[FailureRecord]:
    """返回可入图谱的记录；operational 返回 None（只应进运行日志）。"""
    if not admits_to_atlas(record):
        return None
    _check_context(record)
    return record


def partition(records: List[FailureRecord]) -> Dict[str, List[FailureRecord]]:
    """拆成图谱与日志两堆，供写入层消费。"""
    atlas = []
    log = []
    for record in records:
        if admits_to_atlas(record):
            _check_context(record)
            atlas.append(record)
        else:
            log.append(record)
    return {"atlas": atlas, "log": log}


def summarize(records: List[FailureRecord]) -> Dict[str, int]:
    """按 kind 计数，便于 query pack 引用。"""
    counts = {}
    for record in records:
        counts[record.kind] = counts.get(record.kind, 0) + 1
    return counts
