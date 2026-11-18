"""Typed research memory: nodes, edges, admission, staleness, budgeted packs.

This is the memory design the demo was missing. The repo already stores artifacts in
project/runs, but the memory that feeds the *next* research step is scattered across
five islands (project artifacts, literature memory, guideline memory, feedback ledger,
verdict ledger). This module makes one typed graph over them:

- a node is one research object (idea / experiment / run / evidence / claim / closure /
  paper audit finding / durable failure / dataset / recipe / decision);
- an edge is one relation a later step can consume (tests / supports / falsifies /
  supersedes / invalidates / depends_on / contradicts / reuses / derived_from);
- every node keeps its source path and sha256, so staleness is mechanical;
- admission decides what may enter a *generation* pack (pending work stays visible to
  reviewers, never injected into generation);
- a pack is deterministic, budgeted, provenance-carrying, and never prunes failures.

It creates no Claim / EA / Verdict / Signature and changes no gate.
"""

import hashlib
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

NODE_TYPES = (
    "idea",
    "experiment",
    "run",
    "evidence",
    "claim",
    "closure",
    "paper",
    "failure",
    "dataset",
    "recipe",
    "decision",
    "finding",
)

RELATIONS = (
    "tests",
    "supports",
    "falsifies",
    "supersedes",
    "invalidates",
    "depends_on",
    "contradicts",
    "reuses",
    "derived_from",
)

STATUSES = ("admitted", "pending", "rejected", "stale")

# Pack section order per research stage. Failures and contradictions always first:
# a step that does not know how the last one failed repeats it.
PACK_ORDER = {
    "idea": ("failures", "contradictions", "scope", "datasets", "recipes", "claims", "ideas"),
    "experiment": ("failures", "contradictions", "datasets", "recipes", "scope", "claims"),
    "paper": ("claims", "failures", "scope", "recipes", "contradictions"),
}

SECTION_BUDGET = {
    "failures": 10 ** 6,   # never pruned
    "contradictions": 10 ** 6,
    "scope": 2400,
    "datasets": 1600,
    "recipes": 1800,
    "claims": 2200,
    "ideas": 1400,
}

DURABLE_FAILURES = (
    "design_flaw",
    "construct_mismatch",
    "underpowered",
    "contamination",
    "leakage",
    "population_drift",
    "true_null",
)


class MemoryGraphError(ValueError):
    pass


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: str) -> str:
    with open(str(path), "rb") as handle:
        return _sha256_bytes(handle.read())


@dataclass(frozen=True)
class MemoryNode:
    node_id: str
    node_type: str
    stage: str
    status: str
    summary: str
    scope: str
    source: str
    sha256: str
    payload: Tuple[Tuple[str, str], ...] = ()
    tags: Tuple[str, ...] = ()

    def __post_init__(self):
        if not self.node_id.strip() or not self.summary.strip():
            raise ValueError("node_id 与 summary 不能为空")
        if self.node_type not in NODE_TYPES:
            raise ValueError("未知 node_type: {0}".format(self.node_type))
        if self.status not in STATUSES:
            raise ValueError("未知 status: {0}".format(self.status))
        if not self.sha256:
            raise ValueError("节点必须带 sha256：没有哈希就无法判定过期")

    def get(self, key: str, default: str = "") -> str:
        for name, value in self.payload:
            if name == key:
                return value
        return default

    def to_dict(self) -> Dict[str, object]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "stage": self.stage,
            "status": self.status,
            "summary": self.summary,
            "scope": self.scope,
            "source": self.source,
            "sha256": self.sha256,
            "payload": dict(self.payload),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "MemoryNode":
        return cls(
            node_id=str(data["node_id"]),
            node_type=str(data["node_type"]),
            stage=str(data["stage"]),
            status=str(data["status"]),
            summary=str(data["summary"]),
            scope=str(data.get("scope") or ""),
            source=str(data["source"]),
            sha256=str(data["sha256"]),
            payload=tuple(sorted((str(k), str(v)) for k, v in dict(data.get("payload") or {}).items())),
            tags=tuple(str(item) for item in (data.get("tags") or [])),
        )


@dataclass(frozen=True)
class MemoryEdge:
    source: str
    target: str
    relation: str
    evidence: str = ""

    def __post_init__(self):
        if self.relation not in RELATIONS:
            raise ValueError("未知 relation: {0}".format(self.relation))

    def to_dict(self) -> Dict[str, str]:
        return {"source": self.source, "target": self.target, "relation": self.relation, "evidence": self.evidence}

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "MemoryEdge":
        return cls(
            source=str(data["source"]),
            target=str(data["target"]),
            relation=str(data["relation"]),
            evidence=str(data.get("evidence") or ""),
        )


@dataclass(frozen=True)
class Admission:
    status: str
    reasons: Tuple[str, ...]


def admit(node: MemoryNode) -> Admission:
    """Decide whether a node may enter a generation pack (fail-closed)."""
    if node.node_type == "claim":
        if node.get("status") == "supported" and node.get("human_reason").strip():
            return Admission("admitted", ("signed claim with human_reason",))
        if node.get("status") == "undecidable":
            return Admission("admitted", ("negative claim: undecidable is a result, not a failure",))
        return Admission("pending", ("claim has no human signature yet",))

    if node.node_type == "idea":
        try:
            evidence_count = int(node.get("evidence_count") or 0)
        except ValueError:
            evidence_count = 0
        if node.get("status") == "selected" and evidence_count >= 1:
            return Admission("admitted", ("selected idea with at least one evidence ref",))
        if node.get("status") == "rejected":
            return Admission("rejected", ("idea was rejected; keep it out of generation",))
        return Admission("pending", ("idea selected status or evidence missing",))

    if node.node_type == "experiment":
        if node.get("status") in ("frozen", "ready_for_g2"):
            return Admission("admitted", ("design is ready for or past G2",))
        return Admission("pending", ("design draft only",))

    if node.node_type == "run":
        if node.get("status") in ("completed", "ok") and node.sha256:
            return Admission("admitted", ("completed run with artifact hash",))
        return Admission("pending", ("run not completed",))

    if node.node_type == "evidence":
        if node.get("status") in ("verified", "completed"):
            return Admission("admitted", ("verified evidence",))
        return Admission("pending", ("evidence not verified",))

    if node.node_type == "closure":
        if node.get("status") in ("ready", "signed"):
            return Admission("admitted", ("closure ready or signed",))
        return Admission("rejected", ("closure blocked; must not be cited as complete",))

    if node.node_type == "failure":
        if node.get("kind") in DURABLE_FAILURES:
            return Admission("admitted", ("durable failure: reusable",))
        return Admission("rejected", ("operational failure: log only, never memory",))

    if node.node_type == "dataset":
        scope_text = node.get("scope") or node.scope
        if node.get("license") and scope_text:
            return Admission("admitted", ("dataset card has license and scope",))
        return Admission("pending", ("dataset card lacks license or scope",))

    if node.node_type == "recipe":
        if node.get("heldout_passed") == "True" and node.get("human_reason"):
            return Admission("admitted", ("recipe passed held-out tasks and was accepted by a human",))
        return Admission("pending", ("recipe has no held-out pass or no human acceptance",))

    if node.node_type == "finding":
        return Admission("admitted", ("review finding: context, not evidence",))

    if node.node_type == "paper":
        return Admission("pending", ("paper projection is derived, never evidence",))

    return Admission("pending", ("no admission rule for {0}".format(node.node_type),))


@dataclass(frozen=True)
class MemoryGraph:
    nodes: Tuple[MemoryNode, ...]
    edges: Tuple[MemoryEdge, ...]
    boundary: str = (
        "read-only typed memory over project artifacts; no Claim/EA/Verdict/Signature is "
        "created, and no gate reads this graph"
    )

    def by_type(self, node_type: str) -> List[MemoryNode]:
        return [node for node in self.nodes if node.node_type == node_type]

    def get(self, node_id: str) -> MemoryNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise MemoryGraphError("unknown node: {0}".format(node_id))

    def counts(self) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for node in self.nodes:
            key = "{0}/{1}".format(node.node_type, node.status)
            out[key] = out.get(key, 0) + 1
        return out

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": "research-memory-graph-0.1",
            "boundary": self.boundary,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "MemoryGraph":
        if str(data.get("schema")) != "research-memory-graph-0.1":
            raise MemoryGraphError("unexpected schema: {0}".format(data.get("schema")))
        return cls(
            nodes=tuple(MemoryNode.from_dict(item) for item in data.get("nodes") or []),
            edges=tuple(MemoryEdge.from_dict(item) for item in data.get("edges") or []),
            boundary=str(data.get("boundary") or ""),
        )


def refresh(graph: MemoryGraph, current_hashes: Dict[str, str]) -> MemoryGraph:
    """Mark nodes stale whose source file changed or disappeared."""
    nodes = []
    for node in graph.nodes:
        current = current_hashes.get(node.source)
        if current is None:
            nodes.append(replace(node, status="stale", tags=tuple(sorted(set(node.tags + ("source_missing",))))))
        elif current != node.sha256:
            nodes.append(replace(node, status="stale", tags=tuple(sorted(set(node.tags + ("source_changed",))))))
        else:
            nodes.append(node)
    return MemoryGraph(nodes=tuple(nodes), edges=graph.edges, boundary=graph.boundary)


@dataclass(frozen=True)
class PackSection:
    name: str
    lines: Tuple[str, ...]
    dropped: int = 0


@dataclass(frozen=True)
class MemoryPack:
    stage: str
    sections: Tuple[PackSection, ...]
    stale_excluded: int
    pending_excluded: int
    total_chars: int
    budget: int

    def render(self) -> str:
        out = ["# MemoryPack ({0}) · read-only, deterministic, with provenance".format(self.stage), ""]
        for section in self.sections:
            if not section.lines:
                continue
            out.append("## {0}".format(section.name))
            out.extend(section.lines)
            if section.dropped:
                out.append("> omitted {0} item(s) for budget".format(section.dropped))
            out.append("")
        out.append(
            "> excluded: stale {0}, pending {1}; size {2}/{3} chars".format(
                self.stale_excluded, self.pending_excluded, self.total_chars, self.budget
            )
        )
        return "\n".join(out).rstrip() + "\n"

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": "research-memory-pack-0.1",
            "stage": self.stage,
            "sections": [
                {"name": s.name, "lines": list(s.lines), "dropped": s.dropped} for s in self.sections
            ],
            "stale_excluded": self.stale_excluded,
            "pending_excluded": self.pending_excluded,
            "total_chars": self.total_chars,
            "budget": self.budget,
            "boundary": "pack is a projection for generation context; it is not evidence and cannot be cited",
        }


def _line(node: MemoryNode) -> str:
    tag_text = "|tags=" + ",".join(node.tags) if node.tags else ""
    return "- [{0}] {1}: {2} | src={3}#{4}{5}".format(
        node.node_type,
        node.node_id,
        " ".join(node.summary.split())[:200],
        node.source,
        node.sha256[:12],
        tag_text,
    )


def build_pack(
    graph: MemoryGraph,
    stage: str,
    budget: int = 8000,
    focus: Optional[str] = None,
) -> MemoryPack:
    """Deterministic budgeted pack for one stage.

    focus (e.g. an idea node id) puts connected nodes first, so the stage receives a
    pack about *this* task rather than the whole project history.
    """
    if stage not in PACK_ORDER:
        raise MemoryGraphError("unknown stage: {0}".format(stage))

    related = set()
    if focus:
        related.add(focus)
        for edge in graph.edges:
            if edge.source == focus:
                related.add(edge.target)
            if edge.target == focus:
                related.add(edge.source)

    admitted = [node for node in graph.nodes if node.status == "admitted"]
    stale = sum(1 for node in graph.nodes if node.status == "stale")
    pending = sum(1 for node in graph.nodes if node.status in ("pending", "rejected"))

    buckets: Dict[str, List[MemoryNode]] = {name: [] for name in PACK_ORDER[stage]}

    def put(section: str, node: MemoryNode) -> None:
        if section in buckets:
            buckets[section].append(node)

    for node in admitted:
        if node.node_type == "failure":
            put("failures", node)
        elif node.node_type == "claim":
            put("claims", node)
            put("scope", node)
        elif node.node_type == "idea":
            put("ideas", node)
        elif node.node_type == "dataset":
            put("datasets", node)
        elif node.node_type == "recipe":
            put("recipes", node)
        elif node.node_type in ("experiment", "run"):
            # prior design/run context is applicability information for later stages
            put("scope", node)

    focus_run = ""
    if focus and "-" in focus:
        parts = focus.split("-")
        for index in range(len(parts)):
            if parts[index] == "RUN" and index + 1 < len(parts):
                focus_run = "RUN-" + parts[index + 1]
                break
    blocked = [
        node
        for node in graph.by_type("finding")
        if node.status == "admitted" and node.get("severity") == "blocker"
        and (not focus_run or node.node_id.startswith(focus_run))
    ]
    contradiction_lines = [_line(node) for node in blocked[:40]]
    for edge in graph.edges:
        if edge.relation in ("contradicts", "falsifies") and (not focus or edge.source in related or edge.target in related):
            contradiction_lines.append(
                "- [{0}] {1} -> {2}: {3}".format(edge.relation, edge.source, edge.target, edge.evidence)
            )

    sections: List[PackSection] = []
    total = 0
    for name in PACK_ORDER[stage]:
        if name == "contradictions":
            body = tuple(contradiction_lines[:60])
            sections.append(PackSection("contradictions", body, max(0, len(contradiction_lines) - len(body))))
            total += sum(len(item) for item in body)
            continue
        nodes = list(buckets.get(name, []))
        nodes.sort(key=lambda node: (0 if node.node_id in related else 1, node.node_id))
        cap = SECTION_BUDGET.get(name, 2000)
        lines: List[str] = []
        used = 0
        dropped = 0
        for node in nodes:
            if name == "scope" and node.node_type == "claim":
                line = "- [scope] {0}: {1} | src={2}#{3}".format(
                    node.node_id, node.scope or "(no scope declared)", node.source, node.sha256[:12]
                )
            elif name == "scope" and node.node_type in ("experiment", "run"):
                line = "- [scope] {0}: {1} | src={2}#{3}".format(
                    node.node_id, node.summary or "(no summary)", node.source, node.sha256[:12]
                )
            else:
                line = _line(node)
            if name not in ("failures", "contradictions") and used + len(line) > min(cap, budget):
                dropped += 1
                continue
            lines.append(line)
            used += len(line)
        sections.append(PackSection(name, tuple(lines), dropped))
        total += used

    return MemoryPack(
        stage=stage,
        sections=tuple(sections),
        stale_excluded=stale,
        pending_excluded=pending,
        total_chars=total,
        budget=budget,
    )


FAILURE_ATLAS_SCHEMA = "failure-atlas-0.1"
FAILURE_REQUIRED_FIELDS = ("failure_id", "kind", "scope", "observed", "diagnosis", "retry_condition")


def load_failure_atlas(path) -> Dict[str, Any]:
    """Load and validate a durable-failure atlas (the machine-readable failure memory).

    The atlas is the input the memory graph was missing: without it, every pack's
    "failures" section is empty and the feedback loops have nothing durable to reuse.
    """
    target = Path(path)
    if not target.is_file():
        raise MemoryGraphError("failure atlas not found: " + str(target))
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MemoryGraphError("cannot read failure atlas: " + str(exc))
    if not isinstance(data, dict) or str(data.get("schema") or "") != FAILURE_ATLAS_SCHEMA:
        raise MemoryGraphError("failure atlas schema must be " + FAILURE_ATLAS_SCHEMA)
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise MemoryGraphError("failure atlas needs a non-empty entries list")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise MemoryGraphError("failure atlas entries must be objects")
        for field in FAILURE_REQUIRED_FIELDS:
            if not str(entry.get(field) or "").strip():
                raise MemoryGraphError("failure atlas entry needs " + field)
        failure_id = str(entry["failure_id"])
        if failure_id in seen:
            raise MemoryGraphError("duplicate failure id: " + failure_id)
        seen.add(failure_id)
        if not isinstance(entry.get("evidence") or [], list):
            raise MemoryGraphError("failure evidence must be a list: " + failure_id)
    return data


def ingest_failure_atlas(path) -> List[MemoryNode]:
    """Turn atlas entries into failure nodes, applying the same admission rules as other nodes."""
    target = Path(path)
    data = load_failure_atlas(target)
    with open(str(target), "rb") as handle:
        digest = _sha256_bytes(handle.read())
    nodes: List[MemoryNode] = []
    for entry in data["entries"]:
        node = MemoryNode(
            node_id=str(entry["failure_id"]),
            node_type="failure",
            stage="META",
            status="pending",
            summary="{0}: {1}".format(entry["kind"], str(entry["diagnosis"])[:180]),
            scope=str(entry["scope"]),
            source=str(target).replace(os.sep, "/"),
            sha256=digest,
            payload=(
                ("kind", str(entry["kind"])),
                ("observed", str(entry["observed"])[:240]),
                ("retry_condition", str(entry["retry_condition"])[:240]),
                ("evidence", ";".join(str(item) for item in entry.get("evidence") or [])[:240]),
            ),
            tags=("failure_atlas",),
        )
        admission = admit(node)
        nodes.append(
            replace(
                node,
                status=admission.status,
                tags=tuple(sorted(set(node.tags + admission.reasons))),
            )
        )
    return nodes


def _stable_id(*parts: str) -> str:
    return "-".join(str(part) for part in parts if str(part).strip())


def default_artifact_files(root: str) -> List[str]:
    """Discover the artifact files this ingester understands under a project root."""
    found: List[str] = []
    runs = os.path.join(root, "runs")
    if not os.path.isdir(runs):
        return found
    for run_name in sorted(os.listdir(runs)):
        run_dir = os.path.join(runs, run_name)
        if not os.path.isdir(run_dir):
            continue
        for name in ("task.json", "idea.json", "experiment.json", "design-audit.json", "manuscript-audit.json"):
            if os.path.isfile(os.path.join(run_dir, name)):
                found.append(os.path.join("runs", run_name, name))
        for name in ("claim.json", "closure-report.json"):
            if os.path.isfile(os.path.join(run_dir, "claim", name)):
                found.append(os.path.join("runs", run_name, "claim", name))
            if os.path.isfile(os.path.join(run_dir, "closure", name)):
                found.append(os.path.join("runs", run_name, "closure", name))
    return found


def ingest_project(
    root: str,
    files: Iterable[str],
    dataset_cards: Sequence[Dict[str, str]] = (),
    failure_atlas: Optional[str] = None,
) -> MemoryGraph:
    """Ingest known artifact files under a project root into a typed graph.

    failure_atlas is optional on purpose: a project without recorded durable failures is a
    legitimate (and measurable) state, not an error.
    """
    nodes: List[MemoryNode] = []
    edges: List[MemoryEdge] = []
    seen: Dict[str, str] = {}

    def add(node: MemoryNode) -> None:
        if node.node_id in seen:
            raise MemoryGraphError("duplicate node id: {0}".format(node.node_id))
        seen[node.node_id] = node.node_type
        admission = admit(node)
        nodes.append(
            replace(node, status=admission.status, tags=tuple(sorted(set(node.tags + admission.reasons))))
        )

    for relative in files:
        relative = str(relative).replace(os.sep, "/").replace("\\", "/")
        path = os.path.join(root, relative)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            raw = handle.read()
        digest = _sha256_bytes(raw)
        try:
            data = json.loads(raw.decode("utf-8"))
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        run_id = ""
        parts = relative.replace("\\", "/").split("/")
        if "runs" in parts:
            index = parts.index("runs")
            if index + 1 < len(parts):
                run_id = parts[index + 1]

        name = os.path.basename(relative)

        if name == "task.json":
            plan = data.get("plan") or {}
            add(MemoryNode(
                node_id=_stable_id(run_id, "run", str(data.get("task_id") or "task")[:10]),
                node_type="run",
                stage="S0-S1",
                status="pending",
                summary="{0} | route={1} | deliverable={2}".format(
                    str(plan.get("goal") or "")[:120],
                    plan.get("route") or "",
                    plan.get("deliverable") or "",
                ),
                scope=str(plan.get("venue_type") or ""),
                source=relative,
                sha256=digest,
                payload=(
                    ("status", str(data.get("status") or "")),
                    ("route", str(plan.get("route") or "")),
                    ("flow_mode", str(plan.get("flow_mode") or "")),
                    ("gates", ",".join(str(item) for item in plan.get("human_gates") or [])),
                    ("steps", str(len(data.get("steps") or []))),
                ),
            ))

        elif name == "idea.json":
            for candidate in data.get("candidates") or []:
                idea_id = str(candidate.get("idea_id") or "")
                if not idea_id:
                    continue
                add(MemoryNode(
                    node_id=_stable_id(run_id, "idea", idea_id),
                    node_type="idea",
                    stage="S2-S3",
                    status="pending",
                    summary="{0} {1}".format(
                        str(candidate.get("title") or "")[:80],
                        str(candidate.get("hypothesis") or "")[:120],
                    ),
                    scope=str(candidate.get("relation_type") or ""),
                    source=relative,
                    sha256=digest,
                    payload=(
                        ("status", str(candidate.get("status") or "")),
                        ("evidence_count", str(candidate.get("evidence_count") or 0)),
                        ("lens", str(candidate.get("lens") or "")),
                        ("testability", str(candidate.get("testability") or "")),
                        ("falsification", str(candidate.get("falsification") or "")[:200]),
                    ),
                ))

        elif name == "experiment.json":
            design_id = str(data.get("design_id") or "")
            idea_id = str(data.get("idea_id") or "")
            node_id = _stable_id(run_id, "experiment", design_id[:10] or "design")
            add(MemoryNode(
                node_id=node_id,
                node_type="experiment",
                stage="S4",
                status="pending",
                summary="{0} | metric={1} | seeds={2}".format(
                    str(data.get("question") or "")[:90],
                    data.get("primary_metric") or "",
                    data.get("seeds") or "",
                ),
                scope=str(data.get("budget") or ""),
                source=relative,
                sha256=digest,
                payload=(
                    ("status", str(data.get("status") or "")),
                    ("primary_metric", str(data.get("primary_metric") or "")),
                    ("seeds", str(data.get("seeds") or "")),
                    ("idea_id", idea_id),
                ),
            ))
            if idea_id:
                edges.append(
                    MemoryEdge(node_id, _stable_id(run_id, "idea", idea_id), "tests", "experiment.json idea_id")
                )

        elif name == "claim.json":
            claim_id = str(data.get("claim_id") or "")
            if not claim_id:
                continue
            node_id = _stable_id(run_id, "claim", claim_id)
            add(MemoryNode(
                node_id=node_id,
                node_type="claim",
                stage="S5b",
                status="pending",
                summary=str(data.get("statement") or "")[:180],
                scope=str(data.get("scope") or ""),
                source=relative,
                sha256=digest,
                payload=(
                    ("status", str(data.get("status") or "")),
                    ("human_reason", str(data.get("human_reason") or "")),
                    ("claim_type", str(data.get("claim_type") or "")),
                    ("evidence_refs", ",".join(str(item) for item in data.get("evidence_refs") or [])),
                ),
            ))
            run_ref = str((data.get("verification") or {}).get("run_id") or "")
            if run_ref:
                edges.append(
                    MemoryEdge(node_id, _stable_id(run_id, "run", run_ref), "derived_from", "verification.run_id")
                )

        elif name == "closure-report.json":
            report_id = str(data.get("report_id") or "")
            node_id = _stable_id(run_id, "closure", report_id[:10] or "closure")
            failed = sum(1 for check in data.get("checks") or [] if check.get("status") == "fail")
            add(MemoryNode(
                node_id=node_id,
                node_type="closure",
                stage="S13-S16",
                status="pending",
                summary="closure status={0} checks={1} failed={2}".format(
                    data.get("status") or "", len(data.get("checks") or []), failed
                ),
                scope=str(data.get("closure_profile") or ""),
                source=relative,
                sha256=digest,
                payload=(("status", str(data.get("status") or "")), ("failed_checks", str(failed))),
            ))

        elif name == "design-audit.json":
            for check in data.get("checks") or []:
                if check.get("status") != "warn":
                    continue
                check_id = str(check.get("id") or "")
                add(MemoryNode(
                    node_id=_stable_id(run_id, "finding", "design", check_id),
                    node_type="finding",
                    stage="S4",
                    status="pending",
                    summary="{0}: {1}".format(check_id, str(check.get("detail") or "")[:160]),
                    scope=str(check.get("severity") or "warning"),
                    source=relative,
                    sha256=digest,
                    payload=(("severity", str(check.get("severity") or "warning")), ("check_id", check_id)),
                ))

        elif name == "manuscript-audit.json":
            for blocker in data.get("blockers") or []:
                key = str(blocker).split(":")[0]
                add(MemoryNode(
                    node_id=_stable_id(run_id, "finding", "paper", key),
                    node_type="finding",
                    stage="S8-S12",
                    status="pending",
                    summary=str(blocker)[:180],
                    scope="blocker",
                    source=relative,
                    sha256=digest,
                    payload=(("severity", "blocker"), ("check_id", key)),
                ))

    for card in dataset_cards:
        add(MemoryNode(
            node_id=_stable_id("dataset", str(card.get("name") or "")),
            node_type="dataset",
            stage="META",
            status="pending",
            summary="{0}: {1}".format(card.get("name") or "", card.get("known_biases") or ""),
            scope=str(card.get("scope") or ""),
            source=str(card.get("source") or ""),
            sha256=str(card.get("sha256") or _sha256_bytes(json.dumps(card, sort_keys=True).encode("utf-8"))),
            payload=(
                ("license", str(card.get("license") or "")),
                ("sampling", str(card.get("sampling") or "")),
                ("time_split", str(card.get("time_split") or "")),
            ),
        ))

    if failure_atlas:
        for node in ingest_failure_atlas(failure_atlas):
            if node.node_id in seen:
                raise MemoryGraphError("duplicate node id: {0}".format(node.node_id))
            seen[node.node_id] = node.node_type
            nodes.append(node)

    return MemoryGraph(nodes=tuple(nodes), edges=tuple(edges))
