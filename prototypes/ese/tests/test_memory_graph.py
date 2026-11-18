"""Contract tests for the typed research-memory graph."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prototypes.ese.memory_graph import (
    MemoryEdge,
    MemoryGraph,
    MemoryNode,
    MemoryGraphError,
    admit,
    build_pack,
    default_artifact_files,
    ingest_project,
    refresh,
)


def _node(node_type="claim", status="pending", summary="s", scope="S5/demo/iris", payload=(), tags=()):
    return MemoryNode(
        node_id="n-" + node_type,
        node_type=node_type,
        stage="S5",
        status=status,
        summary=summary,
        scope=scope,
        source="runs/R1/x.json",
        sha256="a" * 64,
        payload=payload,
        tags=tags,
    )


class AdmissionTest(unittest.TestCase):
    def test_claim_needs_signature(self):
        unsigned = _node("claim", payload=(("status", "supported"), ("human_reason", "")))
        self.assertEqual(admit(unsigned).status, "pending")
        signed = _node("claim", payload=(("status", "supported"), ("human_reason", "checked scope")))
        self.assertEqual(admit(signed).status, "admitted")

    def test_undecidable_is_a_result_not_a_failure(self):
        node = _node("claim", payload=(("status", "undecidable"), ("human_reason", "honest negative")))
        self.assertEqual(admit(node).status, "admitted")

    def test_durable_failure_admitted_operational_rejected(self):
        durable = _node("failure", payload=(("kind", "underpowered"),))
        self.assertEqual(admit(durable).status, "admitted")
        operational = _node("failure", payload=(("kind", "rate_limit"),))
        self.assertEqual(admit(operational).status, "rejected")

    def test_recipe_needs_heldout_and_human(self):
        pending = _node("recipe", payload=(("heldout_passed", "True"), ("human_reason", "")))
        self.assertEqual(admit(pending).status, "pending")
        admitted = _node("recipe", payload=(("heldout_passed", "True"), ("human_reason", "reviewed")))
        self.assertEqual(admit(admitted).status, "admitted")

    def test_dataset_needs_license_and_scope(self):
        no_license = _node("dataset", payload=(("license", ""),))
        self.assertEqual(admit(no_license).status, "pending")
        complete = _node("dataset", payload=(("license", "Apache-2.0"),))
        self.assertEqual(admit(complete).status, "admitted")

    def test_closure_blocked_is_rejected(self):
        blocked = _node("closure", payload=(("status", "blocked"),))
        self.assertEqual(admit(blocked).status, "rejected")


class RefreshTest(unittest.TestCase):
    def test_unchanged_hash_keeps_status(self):
        graph = MemoryGraph(nodes=(_node("claim", status="admitted"),), edges=())
        same = refresh(graph, {"runs/R1/x.json": "a" * 64})
        self.assertEqual(same.nodes[0].status, "admitted")

    def test_changed_hash_marks_stale(self):
        graph = MemoryGraph(nodes=(_node("claim", status="admitted"),), edges=())
        changed = refresh(graph, {"runs/R1/x.json": "b" * 64})
        self.assertEqual(changed.nodes[0].status, "stale")
        self.assertIn("source_changed", changed.nodes[0].tags)

    def test_missing_source_marks_stale(self):
        graph = MemoryGraph(nodes=(_node("claim", status="admitted"),), edges=())
        missing = refresh(graph, {})
        self.assertEqual(missing.nodes[0].status, "stale")
        self.assertIn("source_missing", missing.nodes[0].tags)


def _failure(index, summary):
    return MemoryNode(
        node_id="failure-{0}".format(index),
        node_type="failure",
        stage="META",
        status="admitted",
        summary=summary,
        scope="Defects4J",
        source="memory/failures.json",
        sha256="c" * 64,
        payload=(("kind", "leakage"),),
    )


class PackTest(unittest.TestCase):
    def test_failures_are_never_pruned(self):
        nodes = tuple(_failure(i, "duplicate test leakage {0}".format(i)) for i in range(40))
        graph = MemoryGraph(nodes=nodes, edges=())
        pack = build_pack(graph, "idea", budget=200)
        failures = [section for section in pack.sections if section.name == "failures"][0]
        self.assertEqual(len(failures.lines), 40)
        self.assertEqual(failures.dropped, 0)

    def test_pending_and_stale_are_excluded_and_counted(self):
        nodes = (
            _node("claim", status="admitted", payload=(("status", "supported"), ("human_reason", "ok"))),
            _node("claim", status="pending"),
            MemoryNode(
                node_id="stale-1", node_type="claim", stage="S5", status="stale", summary="s",
                scope="", source="runs/R1/x.json", sha256="a" * 64,
            ),
        )
        pack = build_pack(MemoryGraph(nodes=nodes, edges=()), "paper")
        self.assertEqual(pack.pending_excluded, 1)
        self.assertEqual(pack.stale_excluded, 1)
        rendered = pack.render()
        self.assertIn("excluded: stale 1, pending 1", rendered)

    def test_pack_order_starts_with_failures(self):
        graph = MemoryGraph(nodes=(_failure(1, "leak"),), edges=())
        pack = build_pack(graph, "experiment")
        self.assertEqual(pack.sections[0].name, "failures")

    def test_focus_prioritises_connected_node(self):
        idea = MemoryNode(
            node_id="R1-idea-IDEA-01", node_type="idea", stage="S2", status="admitted",
            summary="first", scope="", source="runs/R1/idea.json", sha256="d" * 64,
            payload=(("evidence_count", "1"), ("status", "selected")),
        )
        other = MemoryNode(
            node_id="R1-idea-IDEA-02", node_type="idea", stage="S2", status="admitted",
            summary="second", scope="", source="runs/R1/idea.json", sha256="d" * 64,
            payload=(("evidence_count", "2"), ("status", "selected")),
        )
        graph = MemoryGraph(nodes=(other, idea), edges=())
        pack = build_pack(graph, "idea", focus="R1-idea-IDEA-01")
        ideas = [section for section in pack.sections if section.name == "ideas"][0]
        self.assertTrue(ideas.lines[0].startswith("- [idea] R1-idea-IDEA-01"))

    def test_experiment_and_run_appear_as_scope_context(self):
        experiment = MemoryNode(
            node_id="R1-experiment-DESIGN", node_type="experiment", stage="S4", status="admitted",
            summary="q | metric=accuracy | seeds=3", scope="3x", source="runs/R1/experiment.json",
            sha256="e" * 64,
        )
        graph = MemoryGraph(nodes=(experiment,), edges=())
        pack = build_pack(graph, "paper")
        scope = [section for section in pack.sections if section.name == "scope"][0]
        self.assertEqual(len(scope.lines), 1)
        self.assertIn("[scope] R1-experiment-DESIGN", scope.lines[0])

    def test_unknown_stage_is_rejected(self):
        with self.assertRaises(MemoryGraphError):
            build_pack(MemoryGraph(nodes=(), edges=()), "nonsense")


class FailureAtlasTest(unittest.TestCase):
    def _write(self, entries, schema="failure-atlas-0.1"):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"schema": schema, "entries": entries}, tmp)
        tmp.close()
        self.addCleanup(lambda: os.unlink(tmp.name))
        return tmp.name

    def test_durable_failures_are_admitted(self):
        from prototypes.ese.memory_graph import ingest_failure_atlas

        path = self._write([
            {
                "failure_id": "FA-1",
                "kind": "leakage",
                "scope": "Defects4J",
                "observed": "duplicate tests",
                "diagnosis": "fix diff leaked",
                "retry_condition": "dedup and hide diff",
                "evidence": ["tests/test_x.py"],
            },
            {
                "failure_id": "FA-2",
                "kind": "rate_limit",
                "scope": "API",
                "observed": "HTTP 429",
                "diagnosis": "throttled",
                "retry_condition": "back off",
            },
        ])
        nodes = ingest_failure_atlas(path)
        self.assertEqual([node.status for node in nodes], ["admitted", "rejected"])
        self.assertEqual(nodes[0].get("kind"), "leakage")

    def test_repository_atlas_loads_and_is_admitted(self):
        from prototypes.ese.memory_graph import ingest_failure_atlas

        path = ROOT / "research_agent" / "failures" / "atlas.json"
        nodes = ingest_failure_atlas(str(path))
        self.assertGreaterEqual(len(nodes), 6)
        self.assertTrue(all(node.status == "admitted" for node in nodes))

    def test_bad_schema_is_rejected(self):
        from prototypes.ese.memory_graph import MemoryGraphError, load_failure_atlas

        path = self._write([], schema="wrong")
        with self.assertRaises(MemoryGraphError):
            load_failure_atlas(path)

    def test_entry_missing_fields_is_rejected(self):
        from prototypes.ese.memory_graph import MemoryGraphError, load_failure_atlas

        path = self._write([{"failure_id": "FA-1", "kind": "leakage"}])
        with self.assertRaises(MemoryGraphError):
            load_failure_atlas(path)

    def test_project_ingest_includes_atlas_failures(self):
        from prototypes.ese.memory_graph import ingest_project

        atlas = self._write([
            {
                "failure_id": "FA-9",
                "kind": "underpowered",
                "scope": "iris",
                "observed": "CI crosses zero",
                "diagnosis": "n too small",
                "retry_condition": "n>=64",
            }
        ])
        graph = ingest_project(str(ROOT), [], failure_atlas=atlas)
        self.assertEqual([node.node_id for node in graph.by_type("failure")], ["FA-9"])
        pack = build_pack(graph, "idea")
        failures = [section for section in pack.sections if section.name == "failures"][0]
        self.assertEqual(len(failures.lines), 1)


class IngestTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="memory-graph-")
        run_dir = os.path.join(self.tmp, "runs", "RUN-T1")
        os.makedirs(os.path.join(run_dir, "claim"))
        idea = {
            "candidates": [
                {"idea_id": "IDEA-01", "title": "t", "hypothesis": "h", "status": "selected",
                 "evidence_count": 2, "lens": "mechanism", "testability": "needs_metric",
                 "falsification": "f", "relation_type": "single_source"}
            ]
        }
        experiment = {"design_id": "DESIGN-1", "idea_id": "IDEA-01", "question": "q",
                      "primary_metric": "accuracy", "seeds": 3, "budget": "3x", "status": "ready_for_g2"}
        claim = {"claim_id": "CLM-1", "statement": "s", "scope": "S5/demo/iris", "status": "supported",
                 "human_reason": "checked", "claim_type": "numerical", "evidence_refs": ["EA-1"],
                 "verification": {"run_id": "RUN-1"}}
        with open(os.path.join(run_dir, "idea.json"), "w", encoding="utf-8") as handle:
            json.dump(idea, handle)
        with open(os.path.join(run_dir, "experiment.json"), "w", encoding="utf-8") as handle:
            json.dump(experiment, handle)
        with open(os.path.join(run_dir, "claim", "claim.json"), "w", encoding="utf-8") as handle:
            json.dump(claim, handle)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ingest_builds_nodes_and_edges(self):
        files = default_artifact_files(self.tmp)
        self.assertEqual(len(files), 3)
        graph = ingest_project(self.tmp, files)
        types = sorted(node.node_type for node in graph.nodes)
        self.assertEqual(types, ["claim", "experiment", "idea"])
        edge = [edge for edge in graph.edges if edge.relation == "tests"][0]
        self.assertEqual(edge.target, "RUN-T1-idea-IDEA-01")
        claim = [node for node in graph.nodes if node.node_type == "claim"][0]
        self.assertEqual(claim.status, "admitted")
        self.assertTrue(all("/" in node.source and "\\" not in node.source for node in graph.nodes))

    def test_roundtrip(self):
        graph = ingest_project(self.tmp, default_artifact_files(self.tmp))
        again = MemoryGraph.from_dict(json.loads(json.dumps(graph.to_dict())))
        self.assertEqual(len(again.nodes), len(graph.nodes))
        self.assertEqual(len(again.edges), len(graph.edges))


if __name__ == "__main__":
    unittest.main()
