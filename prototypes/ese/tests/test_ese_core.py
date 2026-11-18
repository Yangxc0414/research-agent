import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prototypes.ese import (
    Advice,
    ClaimSpec,
    ClaimState,
    DatasetCard,
    DesignFreeze,
    EvidenceAxis,
    FailureRecord,
    LifecycleError,
    MemoryIndex,
    PluginKind,
    PluginManifest,
    ReproAxis,
    Severity,
    ThreatKind,
    ThreatStance,
    ThreatStatus,
    ValidityThreat,
    advance,
    blockers,
    build_query_pack,
    classify,
    compose,
    to_memory,
)
from prototypes.ese.failure_taxonomy import FailureKindError


def _threats(status=ThreatStatus.MITIGATED):
    return tuple(
        ValidityThreat(kind=kind, status=status, note="已核对")
        for kind in ThreatKind
    )


def _spec(**overrides):
    base = {
        "claim_id": "CLM-1",
        "construct": "代码可维护性",
        "operationalization": "SonarQube maintainability rating",
        "population": "Apache Java 项目 2015-2023",
        "comparison": "重构 vs 不重构",
        "metric": "delta_maintainability",
        "threshold": 0.10,
        "scope": "Apache Java 项目；不外推到 Python",
        "threats": _threats(),
    }
    base.update(overrides)
    return ClaimSpec(**base)


def _state_at_specified():
    return advance(ClaimState(spec=_spec(), stage="proposed"), "specified")


def _state_at_designed():
    design = DesignFreeze(
        sampling_plan="分层随机抽样 64 个项目",
        power_analysis="n=64 达 80% 功效，最小可检效应 0.10",
        analysis_plan="配对 t 检验 + bootstrap 95% CI",
        stopping_rule="区间跨零即报 undecidable；不追跑到显著",
        frozen=True,
    )
    return advance(_state_at_specified(), "designed", design=design)


def _state_at_executed():
    return advance(
        _state_at_designed(),
        "executed",
        run_id="RUN-1",
        env_fingerprint="py3.8/sklearn1.0/sha256:abc",
    )


def _state_at_verified(evidence=EvidenceAxis.SUPPORTED, repro=ReproAxis.REPRODUCED):
    return advance(_state_at_executed(), "verified", evidence=evidence, repro=repro)


def _method_plugin(**overrides):
    base = {
        "plugin_id": "repository-mining",
        "kind": PluginKind.METHOD,
        "hooks": ("specified", "designed", "verified"),
        "provides": ("sampling_plan", "threat_template"),
        "supports": ("样本范围内的方向",),
        "cannot_support": ("跨生态泛化",),
        "returns_to": "designed",
        "writes": ("design/",),
        "forbidden": ("create_claim", "sign", "change_gate"),
        "threat_stances": (
            ThreatStance(ThreatKind.EXTERNAL, Severity.LOW, Advice.ACCEPT),
            ThreatStance(ThreatKind.CONSTRUCT, Severity.MEDIUM, Advice.DECLARE),
            ThreatStance(ThreatKind.CONCLUSION, Severity.MEDIUM, Advice.MITIGATE),
        ),
    }
    base.update(overrides)
    return PluginManifest(**base)


def _task_plugin(**overrides):
    base = {
        "plugin_id": "defect-prediction",
        "kind": PluginKind.TASK,
        "hooks": ("specified", "designed", "verified"),
        "provides": ("baselines", "failure_patterns"),
        "supports": ("该基准上的缺陷倾向",),
        "cannot_support": ("跨项目迁移的因果解释",),
        "returns_to": "verified",
        "writes": ("wiki/",),
        "forbidden": ("create_claim", "sign", "change_gate"),
        "threat_stances": (
            ThreatStance(ThreatKind.EXTERNAL, Severity.HIGH, Advice.REDESIGN),
        ),
        "failure_patterns": ("class imbalance", "temporal bias"),
    }
    base.update(overrides)
    return PluginManifest(**base)


class ClaimSpecTest(unittest.TestCase):
    def test_requires_all_five_threats(self):
        with self.assertRaises(ValueError):
            _spec(threats=_threats()[:4])

    def test_mitigated_threat_requires_note(self):
        with self.assertRaises(ValueError):
            ValidityThreat(
                kind=ThreatKind.CONSTRUCT,
                status=ThreatStatus.MITIGATED,
                note="   ",
            )

    def test_scope_must_be_specific(self):
        with self.assertRaises(ValueError):
            _spec(scope="general")

    def test_threshold_must_be_finite(self):
        with self.assertRaises(ValueError):
            _spec(threshold=float("inf"))


class LifecycleTest(unittest.TestCase):
    def test_cannot_skip_stage(self):
        state = ClaimState(spec=_spec(), stage="proposed")
        with self.assertRaises(LifecycleError):
            advance(state, "executed")

    def test_design_must_be_frozen(self):
        unfrozen = DesignFreeze(
            sampling_plan="分层抽样",
            power_analysis="n=64",
            analysis_plan="配对 t",
            stopping_rule="区间跨零即停",
            frozen=False,
        )
        with self.assertRaises(LifecycleError):
            advance(_state_at_specified(), "designed", design=unfrozen)

    def test_stopping_rule_is_required(self):
        with self.assertRaises(ValueError):
            DesignFreeze(
                sampling_plan="分层抽样",
                power_analysis="n=64",
                analysis_plan="配对 t",
                stopping_rule="",
                frozen=True,
            )

    def test_verified_requires_repro_or_waiver(self):
        with self.assertRaises(LifecycleError):
            advance(
                _state_at_executed(),
                "verified",
                evidence=EvidenceAxis.SUPPORTED,
            )

    def test_undecidable_cannot_be_signed(self):
        state = _state_at_verified(evidence=EvidenceAxis.UNDECIDABLE)
        with self.assertRaises(LifecycleError):
            advance(state, "signed", human_reason="看过了")

    def test_signed_requires_human_reason(self):
        with self.assertRaises(LifecycleError):
            advance(_state_at_verified(), "signed", human_reason="")

    def test_unmitigated_threat_requires_residual_risk_reason(self):
        threats = tuple(
            ValidityThreat(
                kind=kind,
                status=ThreatStatus.UNMITIGATED
                if kind is ThreatKind.INTERNAL
                else ThreatStatus.MITIGATED,
                note="已核对" if kind is not ThreatKind.INTERNAL else "观察性设计，混杂未控制",
            )
            for kind in ThreatKind
        )
        state = replace(_state_at_verified(), spec=_spec(threats=threats))
        with self.assertRaises(LifecycleError):
            advance(state, "signed", human_reason="核对过")
        signed = advance(
            state,
            "signed",
            human_reason="核对过",
            residual_risk_reason="只声称相关性，不声称因果；团队规模是残余混杂",
        )
        self.assertEqual(signed.stage, "signed")

    def test_scoped_requires_invalidation_conditions(self):
        signed = advance(_state_at_verified(), "signed", human_reason="核对过断言边界")
        with self.assertRaises(LifecycleError):
            advance(signed, "scoped")

    def test_blockers_name_the_missing_obligation(self):
        self.assertIn("run_id", blockers(_state_at_designed()))
        self.assertIn("evidence（证据轴未定）", blockers(_state_at_executed()))

    def test_full_path_reaches_scoped(self):
        signed = advance(_state_at_verified(), "signed", human_reason="核对过断言边界")
        scoped = advance(
            signed,
            "scoped",
            invalidation_conditions=("更换语言或生态即失效",),
        )
        self.assertEqual("scoped", scoped.stage)
        self.assertEqual("supported", scoped.axes()["evidence"])
        self.assertEqual("Apache Java 项目；不外推到 Python", scoped.axes()["scope"])


class FailureTaxonomyTest(unittest.TestCase):
    def _record(self, kind):
        return FailureRecord(
            failure_id="F-{0}".format(kind),
            kind=kind,
            context=(("dataset", "defects4j"), ("overlap_check", "ngram-8")),
            observed="CI 跨零",
            diagnosis="样本不足或真实无效",
            retry_condition="n>=64 时重试",
            scope="Apache Java 缺陷预测",
        )

    def test_operational_failure_does_not_enter_atlas(self):
        self.assertIsNone(to_memory(self._record("rate_limit")))
        self.assertEqual("operational", classify("environment"))

    def test_durable_failure_enters_atlas(self):
        admitted = to_memory(self._record("contamination"))
        self.assertIsNotNone(admitted)

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(FailureKindError):
            classify("vibes")

    def test_contamination_requires_overlap_context(self):
        record = FailureRecord(
            failure_id="F-X",
            kind="contamination",
            context=(("dataset", "humaneval"),),
            observed="分数异常高",
            diagnosis="疑似泄漏",
            retry_condition="none",
            scope="HumanEval",
        )
        with self.assertRaises(ValueError):
            to_memory(record)


class PluginContractTest(unittest.TestCase):
    def test_cannot_support_must_be_non_empty(self):
        with self.assertRaises(ValueError):
            _method_plugin(cannot_support=())

    def test_forbidden_must_cover_claim_sign_gate(self):
        with self.assertRaises(ValueError):
            _task_plugin(forbidden=("create_claim",))

    def test_method_task_conflict_is_reported(self):
        profile = compose((_method_plugin(),), (_task_plugin(),))
        self.assertEqual(1, len(profile.conflicts))
        self.assertTrue(profile.has_blocking_conflict)
        self.assertIn("external", profile.conflicts[0].explain())

    def test_composite_keeps_common_hooks_only(self):
        narrow = _method_plugin(hooks=("specified", "verified"))
        profile = compose((narrow,), (_task_plugin(),))
        self.assertEqual(("specified", "verified"), profile.hooks)


class DatasetCardTest(unittest.TestCase):
    def test_llm_dataset_requires_contamination_note(self):
        with self.assertRaises(ValueError):
            DatasetCard(
                name="HumanEval",
                source="github/openai",
                license="MIT",
                sampling="census",
                subject_kind="llm",
                known_biases=("small",),
            )

    def test_sampling_must_be_known(self):
        with self.assertRaises(ValueError):
            DatasetCard(
                name="X",
                source="y",
                license="MIT",
                sampling="whatever",
                subject_kind="code",
                known_biases=(),
            )


class QueryPackTest(unittest.TestCase):
    def test_failures_are_never_pruned(self):
        records = tuple(
            FailureRecord(
                failure_id="F-{0}".format(i),
                kind="design_flaw",
                context=(("design", "paired"),),
                observed="观测" * 30,
                diagnosis="诊断" * 60,
                retry_condition="换配对设计",
                scope="Apache Java",
            )
            for i in range(30)
        )
        pack = build_query_pack(MemoryIndex(claims=(), failures=records))
        rendered = pack.render()
        for i in range(30):
            self.assertIn("F-{0}".format(i), rendered)

    def test_axes_are_projected_separately(self):
        index = MemoryIndex(claims=(_state_at_verified(),), failures=())
        axes = index.by_axis()
        self.assertEqual(["CLM-1"], axes["evidence"]["supported"])
        self.assertEqual(["CLM-1"], axes["reproducibility"]["reproduced"])
        self.assertEqual(
            ["CLM-1"], axes["scope"]["Apache Java 项目；不外推到 Python"]
        )

    def test_prunes_ideas_before_datasets(self):
        failure = FailureRecord(
            failure_id="F-1",
            kind="design_flaw",
            context=(("design", "paired"),),
            observed="短",
            diagnosis="短",
            retry_condition="none",
            scope="Apache Java",
        )
        card = DatasetCard(
            name="Defects4J",
            source="github",
            license="Apache-2.0",
            sampling="census",
            subject_kind="code",
            known_biases=("Java only",),
        )
        ideas = tuple(("IDEA-{0}".format(i), "候选" * 60) for i in range(20))
        index = MemoryIndex(
            claims=(), failures=(failure,), datasets=(card,), ideas=ideas
        )
        pack = build_query_pack(index, total_budget=300)
        self.assertIn("ideas", pack.pruned)
        bodies = dict(pack.sections)
        self.assertTrue(bodies["datasets"].strip())
        self.assertTrue(bodies["failures"].strip())


if __name__ == "__main__":
    unittest.main()
