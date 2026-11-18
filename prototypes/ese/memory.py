"""三轴记忆索引与 QueryPack 预算组装。

与 MathRSI 的 research-wiki 对齐的部分：
- 失败图谱永不裁剪（最高反重复价值）。
- QueryPack 有硬预算，确定性生成，不做开放式摘要。

ESE 化的部分：
- 三轴分开投影，不合并成一个 status。
- 预算优先级：failures > scope > datasets > papers > ideas。
- 数据集坑（known_biases）单列一节，因为 ESE 的重复踩坑多来自数据而非方法。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .failure_taxonomy import to_memory
from .models import ClaimState, DatasetCard, EvidenceAxis, FailureRecord

TOTAL_BUDGET = 8000

SECTION_BUDGET = {
    "failures": 2000,
    "scope": 1400,
    "datasets": 1000,
    "papers": 1800,
    "ideas": 1200,
}

NEVER_PRUNE = frozenset(("failures",))

PRUNE_ORDER = ("ideas", "papers", "datasets", "scope")


def _clip(text: str, limit: int) -> str:
    flat = " ".join(str(text).split())
    if len(flat) <= limit:
        return flat
    return flat[: max(0, limit - 1)] + "…"


@dataclass(frozen=True)
class QueryPack:
    sections: Tuple[Tuple[str, str], ...]
    pruned: Tuple[str, ...]
    total_chars: int
    over_budget: bool = False

    def render(self) -> str:
        lines = ["# QueryPack（只读投影，按预算生成）", ""]
        for name, body in self.sections:
            if not body.strip():
                continue
            lines.append("## {0}".format(name))
            lines.append(body.rstrip())
            lines.append("")
        if self.pruned:
            lines.append(
                "> 已裁剪：{0}（failures 永不裁剪）".format("、".join(self.pruned))
            )
        if self.over_budget:
            lines.append(
                "> 警告：failures 保留完整导致总量超出预算 {0} 字符；"
                "这是有意的取舍，不是生成失败".format(self.total_chars)
            )
        return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class MemoryIndex:
    claims: Tuple[ClaimState, ...]
    failures: Tuple[FailureRecord, ...]
    datasets: Tuple[DatasetCard, ...] = ()
    papers: Tuple[Tuple[str, str], ...] = ()
    ideas: Tuple[Tuple[str, str], ...] = ()

    def by_axis(self) -> Dict[str, Dict[str, List[str]]]:
        """三轴分别投影。任何轴都不得由另外两轴推导。"""
        evidence = {"supported": [], "not_supported": [], "undecidable": [], "unset": []}
        repro = {
            "reproduced": [],
            "partial": [],
            "failed": [],
            "not_attempted": [],
        }
        scope = {}

        for claim in self.claims:
            claim_id = claim.spec.claim_id
            key = claim.evidence.value if claim.evidence else "unset"
            evidence[key].append(claim_id)
            repro[claim.repro.value].append(claim_id)
            scope.setdefault(claim.spec.scope, []).append(claim_id)

        return {"evidence": evidence, "reproducibility": repro, "scope": scope}

    def scale_claims(self) -> List[ClaimState]:
        return [c for c in self.claims if c.stage == "scoped"]

    def durable_failures(self) -> List[FailureRecord]:
        out = []
        for record in self.failures:
            admitted = to_memory(record)
            if admitted is not None:
                out.append(admitted)
        return out


def _render_failures(records: Sequence[FailureRecord], budget: int) -> str:
    if not records:
        return ""
    ordered = sorted(records, key=lambda r: (r.kind, r.failure_id))
    lines = []
    used = 0
    for record in ordered:
        line = "- [{0}] {1}：{2}｜retry: {3}｜scope: {4}".format(
            record.kind,
            record.failure_id,
            _clip(record.diagnosis, 160),
            _clip(record.retry_condition, 120),
            _clip(record.scope, 100),
        )
        if used + len(line) > budget and lines:
            # 失败图谱不裁剪条目，只压缩描述；因此这里继续追加短行。
            line = "- [{0}] {1}：{2}".format(
                record.kind, record.failure_id, _clip(record.diagnosis, 80)
            )
        lines.append(line)
        used += len(line)
    return "\n".join(lines)


def _render_scope(claims: Sequence[ClaimState], budget: int) -> str:
    lines = []
    used = 0
    for claim in claims:
        if claim.stage not in ("signed", "scoped"):
            continue
        invalidates = "；".join(claim.invalidation_conditions) or "未声明"
        line = "- {0}：{1}｜失效条件：{2}".format(
            claim.spec.claim_id,
            _clip(claim.spec.scope, 120),
            _clip(invalidates, 120),
        )
        if used + len(line) > budget and lines:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines)


def _render_datasets(datasets: Sequence[DatasetCard], budget: int) -> str:
    lines = []
    used = 0
    for card in datasets:
        biases = "、".join(card.known_biases) or "未登记"
        line = "- {0}（{1}）：坑 = {2}".format(
            card.name, card.sampling, _clip(biases, 140)
        )
        if used + len(line) > budget and lines:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines)


def _render_pairs(
    title: str, pairs: Sequence[Tuple[str, str]], budget: int
) -> Tuple[str, bool]:
    lines = []
    used = 0
    pruned = False
    for key, text in pairs:
        line = "- {0}：{1}".format(key, _clip(text, 160))
        if used + len(line) > budget and lines:
            pruned = True
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines), pruned


def build_query_pack(index: MemoryIndex, total_budget: int = TOTAL_BUDGET) -> QueryPack:
    """确定性组装 QueryPack。failures 永不裁剪。"""
    failures = index.durable_failures()
    sections = [
        ("failures", _render_failures(failures, SECTION_BUDGET["failures"])),
        ("scope", _render_scope(index.claims, SECTION_BUDGET["scope"])),
        ("datasets", _render_datasets(index.datasets, SECTION_BUDGET["datasets"])),
    ]

    papers, papers_pruned = _render_pairs(
        "papers", index.papers, SECTION_BUDGET["papers"]
    )
    ideas, ideas_pruned = _render_pairs("ideas", index.ideas, SECTION_BUDGET["ideas"])
    sections.append(("papers", papers))
    sections.append(("ideas", ideas))

    pruned = []
    for name, flag in (("ideas", ideas_pruned), ("papers", papers_pruned)):
        if flag:
            pruned.append(name)

    # 全局预算：只从可裁剪节删，按 PRUNE_ORDER。
    def total() -> int:
        return sum(len(body) for _, body in sections)

    for name in PRUNE_ORDER:
        if total() <= total_budget:
            break
        for i, (section_name, body) in enumerate(sections):
            if section_name != name or not body:
                continue
            lines = body.splitlines()
            while lines and total() > total_budget:
                lines.pop()
                sections[i] = (section_name, "\n".join(lines))
            if section_name not in pruned:
                pruned.append(section_name)

    return QueryPack(
        sections=tuple(sections),
        pruned=tuple(pruned),
        total_chars=total(),
        over_budget=total() > total_budget,
    )


def unset_evidence_claims(index: MemoryIndex) -> List[str]:
    """证据轴未定的断言——它们是最该被推进的"当前义务"。"""
    return [
        claim.spec.claim_id
        for claim in index.claims
        if claim.evidence is None or claim.evidence is EvidenceAxis.UNDECIDABLE
    ]
