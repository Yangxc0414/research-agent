"""ESE 研究循环的教学演示。

重要：本文件的数值全部是**示意**，不是实证结果。演示只证明四件事：
1. 最难关口探针可以在大实验之前把设计打回；
2. 三轴状态可以拒绝签署一条"看起来有提升"的断言；
3. durable 失败可以被下一次研究读取和复用；
4. 元演化候选必须过 held-out 任务与人工理由，不能自己采纳。

运行：
    set PYTHONIOENCODING=utf-8
    python -m prototypes.ese.demo_loop
"""

import sys

from .evolution import (
    EvolutionCandidate,
    ShadowTask,
    evaluate_candidate,
    record_decision,
)
from .failure_taxonomy import partition
from .lifecycle import LifecycleError, advance, describe
from .loop import ThreatProbe, advise_failures, decide, gate_probes
from .memory import MemoryIndex, build_query_pack
from .models import (
    ClaimSpec,
    ClaimState,
    DatasetCard,
    DesignFreeze,
    EvidenceAxis,
    FailureRecord,
    ReproAxis,
    ThreatKind,
    ThreatStatus,
    ValidityThreat,
)

DEMO_NOTE = (
    "教学演示：所有效应量、区间、样本数与成本均为示意值，"
    "不是实证结果；演示只验证语义与门禁行为。"
)


def _line(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def _threats(construct_note, internal_note, external_note, conclusion_note, repro_note):
    return (
        ValidityThreat(ThreatKind.CONSTRUCT, ThreatStatus.MITIGATED, construct_note),
        ValidityThreat(ThreatKind.INTERNAL, ThreatStatus.UNMITIGATED, internal_note),
        ValidityThreat(ThreatKind.EXTERNAL, ThreatStatus.UNMITIGATED, external_note),
        ValidityThreat(ThreatKind.CONCLUSION, ThreatStatus.MITIGATED, conclusion_note),
        ValidityThreat(ThreatKind.REPRODUCIBILITY, ThreatStatus.MITIGATED, repro_note),
    )


def build_claim(scope_suffix=""):
    scope = (
        "Defects4J 2.0, Java 11, 30 project-version pairs, "
        "mutation score with a fixed operator set, model cutoff 2026-01"
    )
    if scope_suffix:
        scope = scope + "; " + scope_suffix
    return ClaimSpec(
        claim_id="CLM-ESE-LLM-TESTS-001",
        construct="test effectiveness",
        operationalization="mutation score = killed mutants / non-equivalent mutants",
        population="Defects4J 2.0 Java projects, 30 project-version pairs",
        comparison="LLM-generated tests vs EvoSuite, budget-matched",
        metric="delta_mutation_score",
        threshold=0.05,
        scope=scope,
        threats=_threats(
            construct_note="mutation score is a proxy; 10% sample manually checked against real bug replay",
            internal_note="compute budget and test flakiness are not yet controlled",
            external_note="Java 11 open-source projects only; no industrial or Python claim",
            conclusion_note="paired design; pre-registered one primary comparison; bootstrap CI",
            repro_note="container, prompts, seeds and dataset hashes are recorded",
        ),
    )


def build_narrow_claim():
    scope = (
        "Defects4J 2.0, Java 11, 12 project-version pairs with >=100 non-equivalent mutants, "
        "mutation score with a fixed operator set, model cutoff 2026-01"
    )
    return ClaimSpec(
        claim_id="CLM-ESE-LLM-TESTS-002",
        construct="test effectiveness on mutation-rich projects",
        operationalization="mutation score with a fixed operator set",
        population="12 Defects4J project-version pairs with >=100 non-equivalent mutants",
        comparison="LLM-generated tests vs EvoSuite, budget-matched and deduplicated",
        metric="delta_mutation_score",
        threshold=0.05,
        scope=scope,
        threats=_threats(
            construct_note="same proxy as the original claim; spot-check only",
            internal_note="dedup and budget matching are now enforced",
            external_note="narrower population; explicitly not a generalization of the original claim",
            conclusion_note="pre-registered on the narrowed population before the rerun",
            repro_note="same container and prompt hash; independent project split",
        ),
    )


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(DEMO_NOTE)

    _line("0. 规格：先把一句模糊的问题变成可检验断言")
    spec = build_claim()
    state = ClaimState(spec=spec, stage="proposed")
    print("claim:", spec.claim_id)
    print("construct:", spec.construct)
    print("operationalization:", spec.operationalization)
    print("scope:", spec.scope)
    print("threshold:", spec.threshold)
    print("threats:", ", ".join(threat.kind.value for threat in spec.threats))
    print("stage:", state.stage)

    _line("1. 最难关口：先跑一个能杀死这条断言的探针")
    leak_probe = ThreatProbe(
        probe_id="P-LEAK-01",
        threat=ThreatKind.INTERNAL,
        question="do generated tests duplicate existing tests or leak the fix?",
        cheapest_test="3-project dedup + diff-overlap probe",
        result="failed",
        evidence="38% of generated tests duplicated existing project tests (illustrative)",
        cost="3 projects x 20 minutes",
    )
    gate = gate_probes([leak_probe])
    print("probe:", leak_probe.probe_id, "->", leak_probe.result)
    print("gate:", gate.allowed, "| action:", gate.action, "| return_to:", gate.return_to)
    for reason in gate.reasons:
        print("  -", reason)

    leakage = FailureRecord(
        failure_id="F-LEAK-001",
        kind="leakage",
        context=(
            ("dataset", "Defects4J 2.0"),
            ("overlap_check", "38% duplicate generated tests; diff overlap 0.21"),
        ),
        observed="generated tests reproduced existing tests or the fix diff",
        diagnosis="the prompt included the full bug-fix commit, so the model could copy the fix",
        retry_condition="deduplicate against the project history and hide the fix diff before retry",
        scope="LLM-generated tests on Defects4J; not a claim about all test generation",
    )
    split = partition([leakage])
    print("atlas:", [record.failure_id for record in split["atlas"]])
    print("advice:", [item.failure_id for item in advise_failures(split["atlas"], keywords=("duplicate",))])

    _line("2. 回到设计：去重 + 隐藏修复 diff + 预注册")
    spec2 = build_claim(scope_suffix="deduplicated against project history; fix diff hidden")
    state = advance(state, "specified", spec=spec2)
    print("stage:", state.stage)
    design = DesignFreeze(
        sampling_plan="30 project-version pairs, stratified by project size and mutant count",
        power_analysis="n=30 paired pairs; detectable effect 0.08 at 80% power (illustrative)",
        analysis_plan="paired bootstrap 95% CI; one pre-registered primary comparison; no subgroup fishing",
        stopping_rule="CI crossing zero is reported as undecidable; no adding pairs until significant",
        frozen=True,
    )
    power_probe = ThreatProbe(
        probe_id="P-POWER-01",
        threat=ThreatKind.CONCLUSION,
        question="is 30 pairs enough to detect the pre-registered effect?",
        cheapest_test="power calculation using pilot variance",
        result="passed",
        evidence="detectable effect 0.08; threshold 0.05 is not powered (illustrative)",
    )
    construct_probe = ThreatProbe(
        probe_id="P-CONSTRUCT-01",
        threat=ThreatKind.CONSTRUCT,
        question="does mutation score track real fault detection?",
        cheapest_test="50-mutant manual replay",
        result="passed",
        evidence="rank correlation 0.71 on the spot-check (illustrative)",
    )
    gate = gate_probes([leak_probe, power_probe, construct_probe])
    print("gate with one failed probe:", gate.allowed, "| action:", gate.action)

    # 重新跑一个通过的去重探针，模拟设计修订后的复检。
    leak_probe_2 = ThreatProbe(
        probe_id="P-LEAK-02",
        threat=ThreatKind.INTERNAL,
        question="did dedup and fix hiding remove the leak?",
        cheapest_test="same 3-project dedup probe",
        result="passed",
        evidence="duplicate rate 2%, diff overlap 0.01 (illustrative)",
    )
    gate = gate_probes([leak_probe_2, power_probe, construct_probe])
    print("gate after redesign:", gate.allowed, "| action:", gate.action)
    state = advance(state, "designed", design=design)
    print("->", describe(state))

    _line("3. 执行：记录 run、环境与数据指纹")
    state = advance(
        state,
        "executed",
        run_id="RUN-ESE-LLM-TESTS-0001",
        env_fingerprint="py3.8/py3.11-toolchain/dataset-sha256:defects4j2.0;container-sha256:demo",
    )
    print("->", describe(state))

    _line("4. 分析：区间跨零，不能签署")
    state = advance(
        state,
        "verified",
        evidence=EvidenceAxis.UNDECIDABLE,
        repro=ReproAxis.PARTIAL,
    )
    decision = decide(state)
    print("->", describe(state))
    print("decision:", decision.status, "| signable:", decision.signable)
    print("next:", decision.next_action)
    try:
        advance(state, "signed", human_reason="looks promising")
    except LifecycleError as exc:
        print("signing refused:", str(exc).split("；")[0])

    underpowered = FailureRecord(
        failure_id="F-POWER-001",
        kind="underpowered",
        context=(("n", "30"), ("required_n", "64"), ("design", "paired")),
        observed="CI [-0.02, +0.09] crosses zero (illustrative)",
        diagnosis="the study cannot distinguish no effect from a small positive effect",
        retry_condition="n>=64 pairs, or pre-register a larger minimum detectable effect",
        scope="Defects4J 2.0 mutation score; not evidence that LLM tests are ineffective",
    )
    split = partition([leakage, underpowered])
    print("atlas:", [record.failure_id for record in split["atlas"]])

    _line("5. 窄化复跑：新断言，而不是把原断言改到显著")
    narrow = build_narrow_claim()
    state2 = ClaimState(spec=narrow, stage="proposed")
    state2 = advance(state2, "specified")
    state2 = advance(
        state2,
        "designed",
        design=DesignFreeze(
            sampling_plan="12 pre-registered mutation-rich pairs",
            power_analysis="n=12 pairs; this is exploratory and is labelled as such",
            analysis_plan="paired bootstrap CI; no pooling with the original 30-pair claim",
            stopping_rule="stop at n=12; no post-hoc expansion; report the interval as-is",
            frozen=True,
        ),
    )
    state2 = advance(
        state2,
        "executed",
        run_id="RUN-ESE-LLM-TESTS-0002",
        env_fingerprint="same container; independent project split",
    )
    state2 = advance(
        state2,
        "verified",
        evidence=EvidenceAxis.SUPPORTED,
        repro=ReproAxis.REPRODUCED,
    )
    state2 = advance(
        state2,
        "signed",
        human_reason="checked the narrowed scope, the interval and the independent replication",
        residual_risk_reason="12 Java pairs only; external validity explicitly limited; mutation score is a proxy",
    )
    state2 = advance(
        state2,
        "scoped",
        invalidation_conditions=(
            "Defects4J version changes",
            "mutation operator set changes",
            "model or prompt changes",
            "population moves outside Java 11 open-source projects",
        ),
    )
    print("->", describe(state2))
    print("note: the original 30-pair claim remains undecidable; the narrower claim is a new claim")

    _line("6. 记忆：失败图谱永不裁剪，下一次研究先读它")
    index = MemoryIndex(
        claims=(state, state2),
        failures=tuple(split["atlas"]),
        datasets=(
            DatasetCard(
                name="Defects4J 2.0",
                source="github.com/rjust/defects4j",
                license="Apache-2.0",
                sampling="census",
                subject_kind="llm",
                known_biases=(
                    "Java only",
                    "temporal drift",
                    "bug-fix commit attribution",
                    "mutants are not real faults",
                ),
                time_split="project-version split; never random commit split",
                contamination_note="check model cutoff vs project dates; hide fix diffs from prompts",
            ),
        ),
        papers=(("just2014", "Defects4J: a database of real faults"),),
        ideas=(("IDEA-01", "budget-matched LLM vs EvoSuite with dedup"),),
    )
    pack = build_query_pack(index, total_budget=1100)
    print(pack.render())

    _line("7. 元演化：从两条同类 durable 失败到框架版本")
    candidate = EvolutionCandidate(
        candidate_id="C-001",
        layer="method_plugin",
        target="benchmark-evaluation",
        change="add a mandatory dedup/fix-leak check before any generated-test score",
        rationale="the same leakage failure appeared in two independent studies",
        source_failures=("F-LEAK-001", "F-LEAK-002"),
        predicted_effect="block the leak earlier; add about 20 minutes per study",
        human_reason="reviewed both failures and accepted the extra check",
    )
    shadow_tasks = [
        ShadowTask("T-01", public_delta=0.10, hidden_delta=0.07, n=12, cost_delta=0.02),
        ShadowTask("T-02", public_delta=0.08, hidden_delta=0.05, n=12, cost_delta=0.02),
    ]
    decision = evaluate_candidate(
        candidate, shadow_tasks, durable_failure_ids=("F-LEAK-001", "F-LEAK-002")
    )
    print("candidate:", candidate.candidate_id, "->", decision.status)
    for reason in decision.reasons:
        print("  -", reason)
    record = record_decision("v0.2", candidate, decision, rollback_to="v0.1")
    print("version:", record.version, "| rollback:", record.rollback_to)

    bad = EvolutionCandidate(
        candidate_id="C-002",
        layer="base",
        target="claim threshold",
        change="lower the gate threshold so more studies pass",
        rationale="too many undecidable results",
        source_failures=("F-POWER-001",),
        predicted_effect="more signed claims",
    )
    print("bad candidate:", evaluate_candidate(bad, shadow_tasks).status, "(touches an immutable surface)")

    public_only = EvolutionCandidate(
        candidate_id="C-003",
        layer="task_plugin",
        target="llm4code",
        change="add a new prompt hint",
        rationale="public benchmark improved",
        source_failures=("F-LEAK-001",),
        predicted_effect="higher public score",
        human_reason="tempting but not tested",
    )
    public_tasks = [
        ShadowTask("T-03", public_delta=0.20, hidden_delta=None, n=8),
        ShadowTask("T-04", public_delta=0.18, hidden_delta=None, n=8),
    ]
    print("public-only candidate:", evaluate_candidate(public_only, public_tasks).status, "(needs held-out tasks)")

    _line("8. 结论")
    print("original claim:", state.stage, "| evidence:", state.evidence.value, "| signable:", decide(state).signable)
    print("narrow claim:", state2.stage, "| evidence:", state2.evidence.value, "| signable:", decide(state2).signable)
    print("atlas failures:", ", ".join(record.failure_id for record in split["atlas"]))
    print("adopted framework change:", record.status, record.candidate_id, "->", record.version)
    print("the framework can say no; that is the point.")


if __name__ == "__main__":
    main()
