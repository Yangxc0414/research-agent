---
protocol_id: PROTO-THESIS-01
schema: thesis-eval-protocol-0.1
title: 准入经验块对想法质量的配对 A/B —— memory-ab 确认性研究
status: draft        # draft → signed（执行前由学生签署并冻结哈希）
created: 2026-11-16
student: (待填)
advisor_second_signer: (待填)
claim_family: THESIS-C1 反馈约束效应
design_type: crossed paired A/B（两会话交叉复现）
system_surface: research_agent.memory_ab（memory-ab-0.2）
primary_outcome: per_slot_score_wide_delta
pairs_target: 12     # Crossing A 6 + Crossing B 6
alpha: 0.05          # 双侧配对 t 区间
min_delta: 0.5       # score_wide 0..5
---

# PROTO-THESIS-01 协议卡（预注册）

> 本卡是人写的预注册承诺：**在数据收集之前**写定问题、假设、设计、分析、决策规则与效度威胁。执行前签署并计算 sha256；分析脚本校验哈希。任何偏离先记 `deviations.md`。本卡不进 `research_agent`（ESE 留在研究层，见 design/80）。

## 1. 背景与试点披露

- M2 试点（2026-11-12/13，`runtime_data/topconf-research-2026/memory/ab.json`）：single-session、n=3、per-slot deltas=[1,1,1]（**零方差**），underpowered 如实触发；without 臂 grounded=0 已确认为 **REF→span 映射 glue gap**（fact-baseline 同日登记），不是真实效应。
- 试点方向已影响 H1 的方向性——**如实披露**。本研究是对**新生成样本**的确认性检验，不是对试点数据的重分析。
- 目的：检验"经准入的经验块（guideline memory）"是否改善候选想法在**系统自带确定性过程检查**上的表现。

## 2. 研究问题

RQ1：在冻结模型权重、宿主供给、同一冻结语料下，注入 guideline 块的生成臂相较无块臂，per-slot `score_wide` 是否更高？

## 3. 假设与机制

- H1（方向性）：with > without，合并均值差 ≥ +0.5（`score_wide`，0..5 整数）。
- 机制：经验块把已采纳的过程教训（来源广度、停止规则具体化、风险命名）带入生成上下文，使这些过程检查更常满足。
- 竞争解释：会话差异、槽位配对错位、生成顺序/上下文漂移、仪器缺陷（grounded 映射）、模板差异。

## 4. 设计（交叉配对 A/B）

- **配对单位**：生成 slot（同一请求下的第 i 个候选）。每 crossing：2 个独立生成请求 × 3 候选 = 6 slot/arm；两 crossing 合计 **12 slot/arm**。
- **处理**：guideline 块（内容由 guideline_memory 快照决定；记录块字符数与 sha256）。**对照**：同一模板、同一命令，仅去掉块（`--no-guidance`）。
- **交叉设计（消除会话×处理混淆）**：
  - Crossing A（项目 P1）：with 臂 = 会话 S1，without 臂 = 会话 S2；请求 1–2。
  - Crossing B（项目 P2）：with 臂 = 会话 S2，without 臂 = 会话 S1；请求 3–4。
  - S1/S2 为两个 distinct host session（标签与获取方式在执行前填入；`--session-host-label` 必填，compare 用 `--sessions multi` 强制互异）。
- **语料**：`research-project/runs/RUN-M2-MULTI` 的冻结 literature（24 来源，span/reference 齐全）。生成是**新样本**（新会话、新采样）。
- **不预注册的**：候选内容语义质量的人工盲评（本协议只测 runtime 确定性检查）。

## 5. 指标

- **主指标（唯一决策指标）**：per-slot `score_wide` 差（with − without，0..5 整数；来自 `per_idea_deltas`）。
- **次指标（探索，不做方向声明）**：六项 rate 的臂级差（`grounded_rate`/`falsifiable_rate`/`executable_plan_rate`/`distinct_sources_mean`/`power_aware_stopping_rate`/`risk_noted_rate`）。
- **上限效应声明**：`grounded/falsifiable/executable` 是系统门，过门想法接近天花板；`score_wide` 的区分度来自 `power_aware_stopping` 与 `risk_noted` 两项。
- **仪器检查（数据收集前必须过）**：
  1. 两臂 literature 文件的 spans/references 映射可用：抽 2 条 idea 验证其 `evidence_refs` 解析出 ≥2 个 distinct `source_id`；
  2. 若某臂 `grounded_rate=0` 而 `evidence_refs` 非空 → 判**仪器缺陷**：grounded 退出分析并记录；若能在首条生成前修复则修复后重来；
  3. 处理保真：从 **innovation review 产物**读取 `guidance_chars`（with>0、without=0）并哈希 guideline 块原文。注意：`memory ab record` 的 CLI 不传 guidance，臂记录里的 `guidance_chars` 恒为 0——**不得**把它当处理证据。

## 6. 执行协议

- 生成（每请求一次；`research_agent memory ab plan` 的官方命令面）：
  - with：`python -m research_agent innovation review --project <P> --run-id RUN-M2-MULTI --rounds 1 --max-ideas 3`
  - without：同命令 + `--no-guidance --output-dir <arm-without>`
  - 每请求用独立 output-dir；两臂除块外**完全相同**（模型、rounds、topic、run-id）。
- 记录：
  - `python -m research_agent memory ab record --project <P> --run-id RUN-M2-MULTI --arm with --ideas-file <with ideas> --literature-file <run literature> --session-host-label <S1>`
  - `python -m research_agent memory ab record --project <P> --arm without ... --session-host-label <S2>`
  - `python -m research_agent memory ab compare --project <P> --sessions multi --output-dir <out>`
- 保留产物：ideas 原文、**both arms 的 innovation review 输出（含 `guidance_chars`）**、literature 文件、`memory/ab.json`、compare 输出、EVAL 报告（`thesis-eval/reports/EVAL-01-*.md`）、协议哈希、deviation 日志。
- 失败处理：生成失败/缺槽**不补位**，记缺失对；缺失对 ≥5 判 underpowered。

## 7. 分析计划（外层脚本 `thesis-eval/analysis/analyze_memory_ab.py`）

- 读两个项目的 `ab.json`；校验 `protocol_sha256`；提取 `per_idea_deltas`。
- 每 crossing：n、均值差、配对 t 95% CI（与系统 `search_lab._paired_diff_interval` 同口径）。
- **零方差退化保护**：sd=0 且 n<12 → 不解读（沿用系统"退化区间"教训）。
- **信息性判据**：CI 宽度 ≤ |均值| 才解读（与系统一致）。
- 合并：12 对合并均值差与 CI（若两 crossing 方差异质则分别报告、不合并）；**符号一致性检查**。
- 不做：p-hacking、事后剔除、更换主指标、可选停止。

## 8. 决策规则（唯一判据，先于数据）

- **supported**：两 crossing 均值差同号且为正；合并均值差 ≥ +0.5；合并 CI 排除 0；无仪器缺陷。
- **not_supported**：合并 CI 信息性且含 0；或两 crossing 符号相反（报告异质，不宣称普遍）。
- **underpowered**：缺失对 ≥5；或合并 n<8；或 CI 宽度 > |均值|；或零方差退化未保护。
- **invalid**：仪器检查失败且窗口内无法修复 → 不得产出方向声明，只记录缺陷。

## 9. 停止规则

固定 12 槽，**不窥探、不因中间结果加样或提前停止**。加样须以新协议（PROTO-02）另行预注册。

## 10. 效度威胁与缓解

| 类别 | 威胁 | 缓解 |
| --- | --- | --- |
| construct | 确定性检查≠想法语义质量；gate 项天花板；grounded 历史 glue gap；score_wide 等权 | 主指标限定为过程检查；仪器检查前置；措辞限定"runtime 自身检查上的差异" |
| internal | slot 配对≠同一想法；生成顺序/上下文漂移；模板差异；会话差异 | 交叉设计；命令/模板/run 固定；两 distinct session；deviation 日志 |
| external | 单语料/主题族；宿主单供给；Windows 环境 | 明确适用范围；不做跨模型外推；PROTO-02 可换语料/供给 |
| conclusion | n=12 小样本；MDE≈0.7–1.0（SD 1.0–1.5 假设）；多重性；度量依赖 | 唯一主指标；次指标探索；退化/信息性保护；MDE 与度量依赖披露 |

## 11. 偏离控制

执行偏离（模板/会话/槽位/命令/窗口）在**数据收集前**写入 `thesis-eval/protocols/PROTO-01-deviations.md` 并重算协议哈希；分析前锁定。分析后发现的偏离只登记、不改判。

## 12. 人工门与签署

- **执行前**：学生签署本卡（姓名/日期）；哈希由分析脚本计算并写入 EVAL 报告。
- **签署路径（执行前锁定，写入偏离日志——不在分析后更换）**：
  - (a) **当前不可用**（2026-11-16 核查）：memory-ab 没有 claim/verdict/lineage 路径——`experiment claim` 要 experiment id、`run claim` 要 RunCapsule/EA、`study claim` 要 study 目录，memory-ab 均不产出。若要 (a)，需最小系统 seam（见下）。
  - (b) **当前唯一可用**：本卡签署页 + 分析报告 + fact-baseline + claim 登记（参照 RUN-M2-MULTI 的 claim-registry 格式）；可审计，但不进 verdict-ledger/lineage。
  - 最小 seam 提案（若走 (a)，需批准并按 SPEC-first 实施）：memory 模块新增 `memory ab claim`/`sign`，claim 内含 ab.json/compare/review 产物哈希与断言，人签后入链，可选接 closure/lineage。**ESE 仍留在本目录，不写进系统。**
- **执行后**：学生签结论、导师二签；无论 supported/not_supported/underpowered **均入链**。

## 13. 附录：系统字段对照

- `memory-ab-0.2`：`arms.{with,without}` = `{n, rates{6}, mean_score_wide, per_idea[{grounded, falsifiable, executable_plan, distinct_sources, power_aware_stopping, risk_noted, score, score_wide}]}`；`comparison` = `{pairs, underpowered, per_idea_deltas[{with,without,delta,gates_only}], sign_counts, direction, reading}`。
- 系统边界原文：`MEMORY_AB_BOUNDARY`、`SINGLE_SESSION_BOUNDARY`（`research_agent/memory_ab.py`）。
- 命令面：`memory ab plan/record/compare`；`--sessions multi` 要求两臂 session label 互异，否则 blocked 不报方向。