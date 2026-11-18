"""ESE 循环与元演化准入的契约测试。"""

import unittest

from prototypes.ese.evolution import (
    EvolutionCandidate,
    ShadowTask,
    evaluate_candidate,
    record_decision,
)
from prototypes.ese.failure_taxonomy import classify
from prototypes.ese.loop import (
    ThreatProbe,
    advise_failures,
    decide,
    gate_probes,
)
from prototypes.ese.models import (
    ClaimSpec,
    ClaimState,
    EvidenceAxis,
    FailureRecord,
    ReproAxis,
    ThreatKind,
    ThreatStatus,
    ValidityThreat,
)


def _spec(scope="Apache Java projects 2015-2023; not Python or closed-source"):
    threats = (
        ValidityThreat(ThreatKind.CONSTRUCT, ThreatStatus.MITIGATED, "metric checked against manual labels"),
        ValidityThreat(ThreatKind.INTERNAL, ThreatStatus.UNMITIGATED, "observational; team size not controlled"),
        ValidityThreat(ThreatKind.EXTERNAL, ThreatStatus.UNMITIGATED, "Java only"),
        ValidityThreat(ThreatKind.CONCLUSION, ThreatStatus.MITIGATED, "paired design; pre-registered single comparison"),
        ValidityThreat(ThreatKind.REPRODUCIBILITY, ThreatStatus.MITIGATED, "data snapshot and environment fingerprint"),
    )
    return ClaimSpec(
        claim_id="CLM-TEST-001",
        construct="maintainability",
        operationalization="SonarQube rating",
        population="Apache Java projects",
        comparison="refactoring vs matched non-refactoring commits",
        metric="delta_maintainability",
        threshold=0.10,
        scope=scope,
        threats=threats,
    )


def _failure(failure_id, kind, diagnosis="diagnosis", scope="Apache Java", context=()):
    return FailureRecord(
        failure_id=failure_id,
        kind=kind,
        context=context,
        observed="observed",
        diagnosis=diagnosis,
        retry_condition="retry after fixing the named condition",
        scope=scope,
    )


class ThreatProbeTest(unittest.TestCase):
    def test_failed_internal_probe_forces_redesign(self):
        probe = ThreatProbe(
            probe_id="P-001",
            threat=ThreatKind.INTERNAL,
            question="do generated tests duplicate existing tests?",
            cheapest_test="3-project dedup probe",
            result="failed",
            evidence="38% of generated tests duplicated existing tests",
        )
        gate = gate_probes([probe])
        self.assertFalse(gate.allowed)
        self.assertEqual(gate.action, "redesign")
        self.assertEqual(gate.return_to, "designed")

    def test_failed_construct_probe_respecifies(self):
        probe = ThreatProbe(
            probe_id="P-002",
            threat=ThreatKind.CONSTRUCT,
            question="does the metric measure the construct?",
            cheapest_test="manual label check on 50 cases",
            result="failed",
            evidence="metric correlates with file size, not review quality",
        )
        gate = gate_probes([probe])
        self.assertFalse(gate.allowed)
        self.assertEqual(gate.action, "respecify")
        self.assertEqual(gate.return_to, "specified")

    def test_inconclusive_probe_stops(self):
        probe = ThreatProbe(
            probe_id="P-003",
            threat=ThreatKind.CONCLUSION,
            question="is the study powered?",
            cheapest_test="power calculation",
            result="inconclusive",
            evidence="no agreed effect size",
        )
        gate = gate_probes([probe])
        self.assertFalse(gate.allowed)
        self.assertEqual(gate.action, "stop")

    def test_all_passed_allows_design(self):
        probe = ThreatProbe(
            probe_id="P-004",
            threat=ThreatKind.REPRODUCIBILITY,
            question="can the harness rebuild the environment?",
            cheapest_test="clean-room rebuild",
            result="passed",
            evidence="container rebuilt and hashes match",
        )
        self.assertTrue(gate_probes([probe]).allowed)

    def test_no_probe_is_rejected(self):
        gate = gate_probes([])
        self.assertFalse(gate.allowed)
        self.assertEqual(gate.action, "stop")

    def test_probe_result_is_fail_closed(self):
        with self.assertRaises(ValueError):
            ThreatProbe(
                probe_id="P-005",
                threat=ThreatKind.EXTERNAL,
                question="q",
                cheapest_test="t",
                result="maybe",
                evidence="e",
            )


class ThreeAxisDecisionTest(unittest.TestCase):
    def test_executed_stage_is_not_ready(self):
        decision = decide(ClaimState(spec=_spec(), stage="executed"))
        self.assertFalse(decision.signable)
        self.assertEqual(decision.status, "not_ready")

    def test_undecidable_evidence_cannot_be_signed(self):
        state = ClaimState(
            spec=_spec(),
            stage="verified",
            evidence=EvidenceAxis.UNDECIDABLE,
            repro=ReproAxis.REPRODUCED,
        )
        decision = decide(state)
        self.assertFalse(decision.signable)
        self.assertEqual(decision.status, "undecidable")

    def test_supported_without_replication_is_pending(self):
        state = ClaimState(
            spec=_spec(),
            stage="verified",
            evidence=EvidenceAxis.SUPPORTED,
            repro=ReproAxis.NOT_ATTEMPTED,
        )
        decision = decide(state)
        self.assertFalse(decision.signable)
        self.assertEqual(decision.status, "pending_replication")

    def test_supported_and_reproduced_is_signable(self):
        state = ClaimState(
            spec=_spec(),
            stage="verified",
            evidence=EvidenceAxis.SUPPORTED,
            repro=ReproAxis.REPRODUCED,
        )
        self.assertTrue(decide(state).signable)


class AtlasAdviceTest(unittest.TestCase):
    def test_only_durable_failures_are_advice(self):
        records = [
            _failure("F-001", "rate_limit"),
            _failure("F-002", "underpowered", diagnosis="n=12 below power", context=(("n", "12"),)),
        ]
        advice = advise_failures(records)
        self.assertEqual([item.failure_id for item in advice], ["F-002"])

    def test_keyword_filters_scope(self):
        records = [
            _failure(
                "F-001",
                "leakage",
                diagnosis="38% duplicate tests",
                scope="Defects4J",
                context=(("dataset", "Defects4J"), ("overlap_check", "duplicate=0.38")),
            ),
            _failure(
                "F-002",
                "underpowered",
                diagnosis="n too small",
                scope="CodeReview",
                context=(("n", "8"),),
            ),
        ]
        advice = advise_failures(records, keywords=("duplicate",))
        self.assertEqual([item.failure_id for item in advice], ["F-001"])

    def test_operational_kind_is_not_memorialized(self):
        self.assertEqual(classify("rate_limit"), "operational")
        self.assertEqual(classify("underpowered"), "durable")
        with self.assertRaises(ValueError):
            classify("unknown_kind")

    def test_leakage_requires_overlap_context(self):
        record = _failure("F-LEAK", "leakage")
        with self.assertRaises(ValueError):
            advise_failures([record])
        complete = FailureRecord(
            failure_id="F-LEAK",
            kind="leakage",
            context=(("dataset", "Defects4J"), ("overlap_check", "duplicate=0.38")),
            observed="duplicate tests",
            diagnosis="fix diff leaked into the prompt",
            retry_condition="dedup and hide the fix diff",
            scope="Defects4J",
        )
        self.assertEqual([item.failure_id for item in advise_failures([complete])], ["F-LEAK"])

    def test_population_drift_requires_time_window(self):
        record = _failure("F-DRIFT", "population_drift")
        with self.assertRaises(ValueError):
            advise_failures([record])


def _candidate(**overrides):
    base = dict(
        candidate_id="C-001",
        layer="method_plugin",
        target="benchmark-evaluation",
        change="add a dedup check before scoring generated tests",
        rationale="the same leakage failure occurred in two studies",
        source_failures=("F-001", "F-002"),
        predicted_effect="fewer false positives; slightly higher cost",
        human_reason="reviewed the two failures and accepted the extra check",
    )
    base.update(overrides)
    return EvolutionCandidate(**base)


def _tasks(public=(0.10, 0.08), hidden=(0.07, 0.05), n=10, cost=0.0):
    return [
        ShadowTask(
            task_id="T-{0}".format(index + 1),
            public_delta=public[index],
            hidden_delta=hidden[index],
            n=n,
            cost_delta=cost,
        )
        for index in range(len(public))
    ]


class EvolutionGateTest(unittest.TestCase):
    def test_candidate_touching_gate_is_rejected(self):
        decision = evaluate_candidate(_candidate(touches=("gate",)), _tasks())
        self.assertEqual(decision.status, "reject")

    def test_candidate_needs_held_out_tasks(self):
        tasks = _tasks(hidden=(None, None))
        decision = evaluate_candidate(_candidate(), tasks)
        self.assertEqual(decision.status, "defer")

    def test_public_gain_without_hidden_transfer_is_rejected(self):
        decision = evaluate_candidate(_candidate(), _tasks(hidden=(0.01, -0.02)))
        self.assertEqual(decision.status, "reject")

    def test_hidden_regression_is_rejected_even_if_mean_positive(self):
        decision = evaluate_candidate(_candidate(), _tasks(hidden=(0.20, -0.01)))
        self.assertEqual(decision.status, "reject")

    def test_candidate_without_human_reason_is_deferred(self):
        decision = evaluate_candidate(_candidate(human_reason=""), _tasks())
        self.assertEqual(decision.status, "defer")

    def test_candidate_with_durable_evidence_is_adopted(self):
        decision = evaluate_candidate(
            _candidate(), _tasks(), durable_failure_ids=("F-001", "F-002")
        )
        self.assertEqual(decision.status, "adopt")

    def test_rationale_may_mention_evidence(self):
        candidate = _candidate(rationale="evidence from two studies supports the new check")
        decision = evaluate_candidate(
            candidate, _tasks(), durable_failure_ids=("F-001", "F-002")
        )
        self.assertEqual(decision.status, "adopt")

    def test_non_durable_failure_is_rejected(self):
        decision = evaluate_candidate(
            _candidate(), _tasks(), durable_failure_ids=("F-001",)
        )
        self.assertEqual(decision.status, "reject")

    def test_cost_without_acceptance_is_rejected(self):
        decision = evaluate_candidate(_candidate(human_reason=""), _tasks(cost=0.5))
        self.assertEqual(decision.status, "reject")

    def test_record_decision_keeps_rollback(self):
        candidate = _candidate()
        decision = evaluate_candidate(candidate, _tasks(), durable_failure_ids=("F-001", "F-002"))
        record = record_decision("v0.2", candidate, decision, rollback_to="v0.1")
        self.assertEqual(record.status, "adopt")
        self.assertEqual(record.rollback_to, "v0.1")


if __name__ == "__main__":
    unittest.main()
