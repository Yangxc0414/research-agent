---
id: ese-core
name: 经验软件工程研究内核（原型）
stage: META
version: 0.3.0
status: draft
prototype: true
registered: false
owner: research-agent
inputs:
  - ClaimSpec
  - DatasetCard
  - FailureRecord
  - PluginManifest
  - ThreatProbe
  - EvolutionCandidate
outputs:
  - ClaimState
  - QueryPack
  - ConflictReport
  - ProbeGate
  - StudyDecision
  - FailureAdvice
  - EvolutionDecision
  - EvolutionRecord
  - MemoryGraph
  - MemoryPack
tools: []
gates:
  - G1
  - G2
  - G5
invariants:
  - 不创建 Claim / EA / Verdict / Signature
  - 三条状态轴不得合并为单一 status
  - operational failure 不得进入失败图谱
  - 插件不得声明空 cannot_support
  - 探针未通过不得冻结设计；失败探针必须回到 designed 或 specified
  - 未缓解威胁必须写 residual_risk_reason 才能签署
  - 预注册必须包含 stopping_rule；没有停止规则不得冻结设计
  - 元演化候选不得触碰 claim/evidence/gate/rubric/signature/export/heldout
  - 元演化必须有 durable 失败来源、held-out 任务与 human_reason；不得自动 adopt
  - 记忆图只读：节点必须带 source + sha256；源变更即 stale，stale/pending 不得进入生成包
  - 失败节永不裁剪；生成包必须带出处与排除计数
---

# 经验软件工程研究内核（原型）

## Purpose

把 MathRSI 的四个机制——义务驱动、局部返回点、能力范围声明、失败即资产——落到**经验软件工程（ESE）**的语义上，作为领域无关内核之外的一层可挂载语义。本原型只解决"一条 ESE 断言怎样被规格化、推进、判负、记忆、复用、演化"，不解决真实数据采集、统计执行与论文写作。

明确不解决：不联网、不跑实验、不生成 Claim/EA/Verdict、不替代 `modules/run` 与 `modules/closure` 的既有人签链。

## Contract

- 输入：`ClaimSpec`、`DatasetCard`、`FailureRecord`、`PluginManifest`、`ThreatProbe`、`EvolutionCandidate`（全部为不可变 dataclass）
- 输出：
  - `ClaimState`（三段结论轴 + 阶段 + 残余风险理由）
  - `QueryPack`（带预算的只读投影）
  - `ConflictReport`（方法插件与任务插件的显式冲突）
  - `ProbeGate`（设计冻结前的最难关口门）
  - `StudyDecision`（三轴派生的下一步，不是判定）
  - `FailureAdvice`（只来自 durable 失败的复用建议）
  - `EvolutionDecision` / `EvolutionRecord`（元演化准入建议与可回滚记录）
- 失败：
  - 规格不完整 → `ValueError`，拒绝创建
  - 非法阶段推进 → `LifecycleError`
  - 未知失败类型 → `ValueError`（fail-closed，不得默认归为 durable）
  - 插件缺 `cannot_support` → `ValueError`
  - 探针结果未知 → `ValueError`
  - 元演化候选触碰不可变面 → `reject`
- 证据边界：只读计算，不写任何 artifact；不创建 Claim / EA / Verdict；不改变门禁语义。

### 三轴状态（不得合并）

| 轴 | 取值 | 语义 |
| --- | --- | --- |
| 证据轴 | `supported` / `not_supported` / `undecidable` | 统计与证据是否支持断言原样（含效应量幅度） |
| 复现轴 | `reproduced` / `partial` / `failed` / `not_attempted` | 独立复现的结果，与证据轴正交 |
| 适用域轴 | 自由文本，必须具体 | population × 语言 × 任务族 × 时间窗 |

一条断言可以是"supported 且未复现、仅适用于 Java 开源项目"。合并成一个 status 会丢掉这个信息。

### 阶段与退出条件

```text
proposed -> specified -> designed -> executed -> verified -> signed -> scoped
```

| 目标阶段 | 退出条件 |
| --- | --- |
| specified | 五类效度威胁齐全；`scope` 非空；阈值有限 |
| designed | 预注册四件套（sampling / power / analysis plan / stopping rule）非空；`design_frozen=True`；最难关口探针全部通过 |
| executed | `run_id` 与 `env_fingerprint` 非空 |
| verified | 证据轴已定；复现轴不得为 `not_attempted`，除非显式 `repro_waived` 且给出理由 |
| signed | `human_reason` 非空；存在未缓解威胁时必须写 `residual_risk_reason`（本原型不校验签名，只校验理由存在） |
| scoped | `scope` 与 `invalidation_conditions` 非空 |

`undecidable` 是合法终点：可以停在 `verified`，但**不得进入 `signed`**。未缓解威胁不是自动拒绝：它是必须被人写明的残余风险，而不是被忽略的空白。

### 最难关口（hardest-threat probe）

ESE 的"最难分支"通常不是一条引理，而是**最可能杀死断言的那个效度威胁**。设计冻结前必须至少跑一个探针：

| 探针结果 | 动作 | 返回点 |
| --- | --- | --- |
| failed + construct | respecify | specified |
| failed + internal/external/conclusion/reproducibility | redesign | designed |
| inconclusive | stop | designed |
| 全部 passed | continue | designed |

探针必须比主实验便宜，并记录 `cheapest_test`、`evidence` 与 `cost`。没有探针就冻结设计，视为 fail-closed。

### 失败分类学

```text
operational（只进运行日志）：environment / data_unavailable / transient / rate_limit
durable（进失败图谱）：design_flaw / construct_mismatch / underpowered /
                        contamination / leakage / population_drift / true_null
```

未知类型 fail-closed。`leakage` 与 `contamination` 分开：前者是时间/重复/特征泄漏，后者是训练语料与基准重叠；修法不同。把一次限流写成"该方法无效"，会让系统永久避开一条可行路线。

### 插件契约（二维）

`METHOD` 插件描述"怎么研究"（controlled-experiment / case-study / repository-mining / benchmark-evaluation / survey），`TASK` 插件描述"研究什么"（defect-prediction / llm4code / code-review / refactoring / flaky-test）。两类可组合；同一威胁给出不同立场时必须报 `Conflict`，不得静默取一。

每个插件必须声明非空 `cannot_support`，这是防止过度宣称的结构性约束。

### 元演化准入

`EvolutionCandidate` 只能改一层：base / method_plugin / task_plugin / dataset_card / workspace。准入规则：

1. 触碰 claim/evidence/gate/rubric/signature/export/heldout → reject；
2. 无 durable 失败来源 → reject；
3. 少于两个 held-out 任务 → defer；
4. public 平均不为正，或 held-out 平均不为正，或任一 held-out 退化 → reject；
5. 成本超过阈值且无人接受 → reject；
6. 没有 `human_reason` → defer；
7. 全过 → adopt（仍由人执行，函数不自动生效）。

### 跨领域挂载

内核不认识"数学"或"软件工程"这些领域名词。它只认五件事：一条断言、三条轴、七个阶段、五类威胁、一组失败类型。领域语义全部由插件注入，因此同一个 harness 可以挂不同领域而不改内核：

| 内核概念 | 数学 | 经验软件工程 |
| --- | --- | --- |
| 断言 | 定理陈述 | 效应量断言（指标 + 比较 + 阈值） |
| 证据轴 | 证明检查通过 / 反例 | 统计检验支持 / 不支持 / 功效不足 |
| 复现轴 | 独立重放 / Lean 重构建 | 独立复现（replication） |
| 适用域 | 定理成立的条件与量词范围 | population × 语言 × 任务族 × 时间窗 |
| 失败类型 | 反例、证明漏洞 | design_flaw / construct_mismatch / underpowered / contamination / leakage / true_null |
| 插件 | 领域归约 + 证书检查器 | 方法范式 + 任务族知识 + 数据集卡 |

新增一个领域只需要提交插件清单（威胁立场 + 失败模式 + 核验器 `supports`/`cannot_support`），不改 `models.py`、`lifecycle.py`、`memory.py`。这是"harness 跨领域"的结构性保证，而不是靠文档声明。

## Current Implementation

- `models.py`：`ClaimSpec` / `ValidityThreat` / `DatasetCard` / `FailureRecord` / `ClaimState` / 枚举
- `lifecycle.py`：七段状态机与退出条件（纯函数）
- `failure_taxonomy.py`：durable/operational 分类与记忆准入（含 leakage / population_drift）
- `plugin_contract.py`：二维插件清单、`supports`/`cannot_support` 校验、冲突检测
- `memory.py`：三轴索引与 `QueryPack` 预算组装（失败图谱永不裁剪）
- `loop.py`：`ThreatProbe` / `ProbeGate` / `StudyDecision` / `FailureAdvice`
- `evolution.py`：`EvolutionCandidate` / `ShadowTask` / `EvolutionDecision` / `EvolutionRecord`
- `demo.py`：线性状态机演示；`demo_loop.py`：含设计回退、不可签署、失败复用、元演化准入的完整叙事
- `memory_graph.py`：类型化研究记忆（12 类节点 / 9 类关系 / 准入 / 哈希过期 / 预算化 MemoryPack），并提供 `scripts/research_memory_scan.py` 在真实项目上只读生成 `memory-graph.json` 与各阶段 pack
- `tests/test_ese_core.py` + `tests/test_ese_loop.py` + `tests/test_memory_graph.py`：69 例契约测试
- 不联网；不读写仓库既有产物；Python 3.8 兼容

## Boundaries

- 本目录是**原型**，未进入 `modules/` 注册表，不参与 `workspace export` 与发布树。
- 不替代 `research_agent.claim` / `closure` / `lineage` 的任何语义；将来晋升为正式模块时，三轴字段应作为既有 claim 的**只读扩展**接入，不得改写既有签名字段。
- 不实现真实统计检验、抽样器、污染检测器；这些属于方法插件，不属于内核。
- 插件只提供知识与模板，不得创建 Claim / 签署 / 改门禁。
- 元演化准入是**建议函数**，不是门禁；adopt 仍由人执行，且必须绑定 held-out 证据与回滚点。

## Minimal Change Workflow

1. 改本 SPEC 的 `Contract` 或 `Changelog`；
2. 改实现，保持 `python -m unittest discover -s prototypes/ese/tests` 通过；
3. 若涉及三轴语义、失败分类或元演化准入，补一条可失败用例；
4. 晋升为正式模块时：复制到 `modules/ese-core/SPEC.md`、注册、跑 `workspace export` 与 `build_release.py --prune`。

## Changelog

- 0.3.0（2026-11-18）：新增类型化研究记忆 `memory_graph.py`（节点/关系/准入/过期/预算化 pack）与 `scripts/research_memory_scan.py`；接入 e2e-closed-loop 真实产物跑通（17 节点 / 3 边 / 三阶段 pack）；测试 69 例。
- 0.2.0（2026-11-18）：增加最难关口探针（`loop.py`）、三轴判定与 durable 失败建议；失败分类学增加 `leakage` / `population_drift`；增加元演化准入（`evolution.py`）与 `demo_loop.py`；测试 52 例；预注册增加 stopping_rule（并补一条必填用例），签署增加未缓解威胁的 residual_risk_reason。
- 0.1.0（2026-11-18）：首版原型。三轴状态、七段生命周期、失败分类学、二维插件契约、QueryPack 预算。
