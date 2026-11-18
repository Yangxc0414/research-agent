# ESE Core（原型）

面向**经验软件工程（Empirical Software Engineering）**的研究语义内核。它不是运行时，
不创建 Claim/EA/Verdict，也不替代 `modules/run` / `modules/closure`；它只把"一条 ESE
断言怎样被规格化、推进、判负、记忆、演化"做成可测试的纯函数。

## 为什么需要它

现有仓库的证据闭合（span-only、hash、gate、lineage）解决的是**过程可信**；
MathRSI 的三层架构解决的是**研究判断**（义务、返回点、能力边界、失败资产）。
ESE 需要两者，但不能把统计判断塞进 LLM 或门禁。这个原型把 ESE 的研究判断抽出来：

- 一条断言 = `ClaimSpec`：构念、操作化、population、comparison、metric、threshold、scope、五类效度威胁
- 三条轴 = 证据 / 复现 / 适用域，不合并成一个 status
- 五个阶段 = proposed → specified → designed → executed → verified → signed → scoped
- 两类失败 = operational（只进日志）/ durable（进图谱，可复用）
- 二维插件 = 方法（怎么研究）× 任务（研究什么），每个插件必须声明 `cannot_support`
- 元演化 = 从 durable 失败到候选改动，必须过 held-out 任务与人的理由

## 运行

```bash
# 需要 Python 3.8
python -m unittest discover -s prototypes/ese/tests -v
python -m prototypes.ese.demo        # 线性状态机演示
python -m prototypes.ese.demo_loop   # 设计回退 + 不可签署 + 失败复用 + 元演化
```

Windows 控制台建议：

```powershell
chcp 65001 > $null
$env:PYTHONIOENCODING = "utf-8"
```

## 演示里发生了什么

`demo_loop.py` 的数值全部是**示意**，不是实证结果。它演示：

1. 一个"生成测试是否优于 EvoSuite"的断言，在最难关口发现 38% 重复测试（示意）→ 设计回退；
2. 修订后执行，区间跨零 → `undecidable`，拒绝签署；
3. 记录 `leakage` 与 `underpowered` 两条 durable 失败，写入 QueryPack；
4. 窄化后的**新断言**（不是把原断言改到显著）在独立复现后可签署；
5. 两条同类 durable 失败触发元演化候选：给 benchmark-evaluation 插件加去重检查；
   候选过 held-out 任务与人的理由才 adopt；碰 gate 的候选 reject，只有 public 提升的候选 defer。

## 边界

- 不联网、不跑实验、不读写仓库既有产物。
- 不实现统计检验；区间/功效由方法插件或既有 `study` 提供。
- 不是产品模块；未注册，不参与 `workspace export` / 发布树。
- 演示中的数字不是证据；只验证语义与门禁行为。

## 研究记忆（memory_graph.py）

```bash
# 只读扫描一个项目：写 <project>/memory/memory-graph.json 与三阶段 pack
python scripts/research_memory_scan.py --project runtime_data/e2e-closed-loop
python scripts/research_memory_scan.py --project runtime_data/e2e-closed-loop --stage idea --json
```

- 12 类节点 / 9 类关系；每个节点必须带 `source` + `sha256`，源变即 stale；
- 准入 fail-closed：pending/stale 可见但不得进入生成包；
- pack 确定性、带预算、带出处；`failures` 与 `contradictions` 永不裁剪；
- 设计说明见 `design/83-`。

## 两张图

- `figures/ese/ese-architecture.png`：内核 + 插件 + 工作区 + 元演化（`make_figure.py`）
- `figures/ese/double-loop.png`：研究循环（已实现）与方法演化循环（roadmap）（`make_figure_loop.py`）

## 与正式仓库的接线（设计见 `design/81-`，叙事与图见 `design/82-`）

| 原型 | 现有资产 |
| --- | --- |
| `ClaimSpec` / 五类威胁 | 可扩展 `experiment` 的 design 字段 |
| `DesignFreeze` | `study_preregistration.py` + `protocol freeze-design` |
| 三轴 / 区间门 | `study_claims.comparison_verdicts` + `search_lab._paired_diff_interval` |
| 复现轴 | `study_replication.py` |
| 执行 capsule | `experiment local-init/approve/run/ingest` + `RunCapsule` |
| 失败图谱 | 新增（当前仓库没有） |
| 元演化 | `rsi` / Harness² 的治理账本，但对象要换成研究方法/插件 |
