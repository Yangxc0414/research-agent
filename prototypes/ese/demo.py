"""ESE 内核演示：一条断言从规格到交付，以及记忆/插件层的实际行为。

运行：
    "D:/Program Files/Python38/python.exe" -m prototypes.ese.demo
"""

from .failure_taxonomy import partition
from .lifecycle import STAGES, advance, blockers, describe
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
from .plugin_contract import (
    Advice,
    PluginKind,
    PluginManifest,
    Severity,
    ThreatStance,
    compose,
)


def _line(title):
    print("\n" + "=" * 68)
    print(title)
    print("=" * 68)


def build_spec():
    threats = (
        ValidityThreat(ThreatKind.CONSTRUCT, ThreatStatus.MITIGATED, "用 SonarQube 评级，与人工评审做过一致性核对"),
        ValidityThreat(ThreatKind.INTERNAL, ThreatStatus.UNMITIGATED, "未控制团队规模与提交频率，属观察性证据"),
        ValidityThreat(ThreatKind.EXTERNAL, ThreatStatus.UNMITIGATED, "仅 Apache Java 项目，不外推到 Python 或工业闭源仓库"),
        ValidityThreat(ThreatKind.CONCLUSION, ThreatStatus.MITIGATED, "n=64，配对设计，bootstrap 95% CI，预注册单次比较"),
        ValidityThreat(ThreatKind.REPRODUCIBILITY, ThreatStatus.MITIGATED, "数据快照 + 环境指纹 + 复现脚本随包"),
    )
    return ClaimSpec(
        claim_id="CLM-ESE-001",
        construct="代码可维护性",
        operationalization="SonarQube maintainability rating（A-E 映射为序数）",
        population="Apache Java 项目，2015-2023，>=50 stars",
        comparison="重构提交 vs 匹配的非重构提交",
        metric="delta_maintainability",
        threshold=0.10,
        scope="Apache Java 项目；不外推到 Python 与闭源工业仓库",
        threats=threats,
    )


def main():
    spec = build_spec()
    state = ClaimState(spec=spec, stage="proposed")

    _line("1. 阶段推进：每一步都先看还缺什么")
    for stage in STAGES[1:]:
        print("当前 {0}，下一阶段 {1} 的缺口：".format(state.stage, stage))
        for item in blockers(state):
            print("  - " + item)
        if stage == "designed":
            state = advance(
                state,
                "designed",
                design=DesignFreeze(
                    sampling_plan="按语言与项目规模分层随机抽样 64 个项目",
                    power_analysis="n=64 在 alpha=0.05 下对 0.10 效应量达 80% 功效",
                    analysis_plan="配对 t 检验 + bootstrap 95% CI；预注册单次比较",
                    stopping_rule="区间跨零即报 undecidable；不因结果不显著而加样本",
                    frozen=True,
                ),
            )
        elif stage == "executed":
            state = advance(
                state,
                "executed",
                run_id="RUN-ESE-0001",
                env_fingerprint="py3.8/sklearn1.0.2/dataset-sha256:9f2c",
            )
        elif stage == "verified":
            state = advance(
                state,
                "verified",
                evidence=EvidenceAxis.SUPPORTED,
                repro=ReproAxis.PARTIAL,
            )
        elif stage == "signed":
            state = advance(
                state,
                "signed",
                human_reason="核对断言数值边界与适用域后签署",
                residual_risk_reason="观察性证据，团队规模未控制；结论只声称 Apache Java 相关性",
            )
        elif stage == "scoped":
            state = advance(
                state,
                "scoped",
                invalidation_conditions=(
                    "更换语言或生态",
                    "SonarQube 规则版本变化超过 2 个大版本",
                ),
            )
        else:
            state = advance(state, stage)
        print("  -> " + describe(state))

    _line("2. 三轴读数：不合并成一个 status")
    for axis, value in state.axes().items():
        print("  {0}: {1}".format(axis, value))

    _line("3. 失败分类：哪些进图谱，哪些只进日志")
    records = [
        FailureRecord(
            failure_id="F-001",
            kind="rate_limit",
            context=(("api", "github-search"),),
            observed="HTTP 429",
            diagnosis="接口限流",
            retry_condition="退避 60s 后重试",
            scope="本次运行",
        ),
        FailureRecord(
            failure_id="F-002",
            kind="underpowered",
            context=(("n", "12"), ("design", "unpaired")),
            observed="CI [-0.03, 0.21] 跨零",
            diagnosis="n=12 远低于 80% 功效所需 64，不能读成无效",
            retry_condition="n>=64 或改配对设计后可重试",
            scope="Apache Java 缺陷预测",
        ),
        FailureRecord(
            failure_id="F-003",
            kind="contamination",
            context=(("dataset", "HumanEval"), ("overlap_check", "ngram-8=0.14")),
            observed="同模型在新私有集上下降 22 分",
            diagnosis="公开基准与训练语料重叠，分数虚高",
            retry_condition="仅在私有留出集上重测",
            scope="LLM4Code 评测",
        ),
    ]
    split = partition(records)
    print("  进图谱（durable）：")
    for record in split["atlas"]:
        print("    + {0} [{1}] {2}".format(record.failure_id, record.kind, record.diagnosis))
    print("  只进日志（operational）：")
    for record in split["log"]:
        print("    - {0} [{1}] {2}".format(record.failure_id, record.kind, record.diagnosis))

    _line("4. 二维插件：方法 × 任务，冲突显式报出")
    method = PluginManifest(
        plugin_id="repository-mining",
        kind=PluginKind.METHOD,
        hooks=("specified", "designed", "verified"),
        provides=("sampling_plan", "threat_template"),
        supports=("样本与抽样框范围内的方向",),
        cannot_support=("跨生态泛化", "因果机制"),
        returns_to="designed",
        writes=("design/",),
        forbidden=("create_claim", "sign", "change_gate"),
        threat_stances=(
            ThreatStance(ThreatKind.EXTERNAL, Severity.LOW, Advice.ACCEPT),
            ThreatStance(ThreatKind.CONSTRUCT, Severity.MEDIUM, Advice.DECLARE),
            ThreatStance(ThreatKind.CONCLUSION, Severity.MEDIUM, Advice.MITIGATE),
        ),
    )
    task = PluginManifest(
        plugin_id="defect-prediction",
        kind=PluginKind.TASK,
        hooks=("specified", "designed", "verified"),
        provides=("baselines", "failure_patterns"),
        supports=("该基准上的缺陷倾向排序",),
        cannot_support=("跨项目迁移的因果解释", "实时预测"),
        returns_to="verified",
        writes=("wiki/",),
        forbidden=("create_claim", "sign", "change_gate"),
        threat_stances=(
            ThreatStance(ThreatKind.EXTERNAL, Severity.HIGH, Advice.REDESIGN),
        ),
        failure_patterns=("class imbalance", "temporal bias", "LOC confound"),
    )
    profile = compose((method,), (task,))
    print("  共同可接入阶段：{0}".format(", ".join(profile.hooks)))
    print("  冲突数：{0}（阻塞：{1}）".format(len(profile.conflicts), profile.has_blocking_conflict))
    for conflict in profile.conflicts:
        print("    ! " + conflict.explain())

    _line("5. QueryPack：失败图谱永不裁剪")
    index = MemoryIndex(
        claims=(state,),
        failures=tuple(records),
        datasets=(
            DatasetCard(
                name="Defects4J 2.0",
                source="github/defects4j",
                license="Apache-2.0",
                sampling="census",
                subject_kind="llm",
                known_biases=("Java only", "temporal drift", "bug-fix commit attribution"),
                time_split="按版本切分 2015 / 2020",
                contamination_note="2020 版本部分测试用例出现在 StarCoder 语料，需私有留出集",
            ),
        ),
        papers=(("vaswani2017", " Transformer 架构；与本课题无关，示例裁剪对象"),),
        ideas=(("IDEA-01", "用因果推断替代相关性度量"),),
    )
    pack = build_query_pack(index, total_budget=900)
    print(pack.render())

    _line("完成")
    print("断言最终阶段：{0}".format(state.stage))
    print("适用域：{0}".format(state.spec.scope))
    print("失效条件：{0}".format("；".join(state.invalidation_conditions)))


if __name__ == "__main__":
    main()
