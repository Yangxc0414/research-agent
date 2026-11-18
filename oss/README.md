# 开源科研智能体参考快照

> 用途：给 `02-` 的需求、`04-` 的流水线、`05-` 的对照与 `07-` 的验证层提供**可本地检索的代码底本**。
> 快照日期：**2026-10-19**；2026-10-23 增补 3 个**策展技能快照**（只保留 README、LICENSE 与代表性 SKILL.md，不是完整仓库）。来源：用户提供的 GitHub ZIP（`main` / `master` 分支）与 GitHub Contents API。
> 证据等级：GitHub 元数据 `[已核验]`（2026-10-19 经 GitHub REST API 核对）；机制描述 `[工程参考]`（读 README、技能文档与关键代码，**未运行**）；覆盖矩阵 `[判断]`（未做 benchmark）。
> 本轮（2026-10-19）逐项核对了 ARIS / AutoResearchClaw / AutoSci / Auto-Empirical / EvoMap 的技能与运行时入口；新增 OpenRSI-Index / RSI-Harness 执行验证快照与 RSI-Anything 多域任务运行时快照。能力矩阵中的四个旧能力格（涉及三个项目）已按代码证据修正，见 §3。
> 外部参照 **PaperBenchX** 未提供本地代码，仅以项目口径列入 `03-` §2.6 与 `07-` §1.2，不进入本地快照计数。

---

## 1. 快照清单

| 本地目录 | 仓库 | Stars | 语言 | 许可证 | Commit | 文件数 | 体积 | 定位 |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | --- |
| `AutoResearchClaw-main/` | [aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) | 14,708 | Python | MIT | `be4ba47` | 756 | 52.6 MB | 23 阶段全流程 + HITL + 引文核验 |
| `autoresearch-master/` | [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | 98,125 | Python | 未声明 | `228791f` | 10 | 0.8 MB | 最小 edit-run-keep 科研循环 |
| `Auto-claude-code-research-in-sleep-main/` | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | 17,689 | Python | MIT | `43a5daf` | 751 | 38.9 MB | Markdown 技能包 + 跨模型评审（ARIS） |
| `Auto-Empirical-Research-Skills-main/` | [brycewang-stanford/Auto-Empirical-Research-Skills](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills) | 4,677 | Stata | NOASSERTION（需核对） | `e0b0c13` | 4,603 | 92.4 MB | 1,107 自有技能 + 23,000+ 生态地图 |
| `SoL-Pi-main/` | [NVlabs/SoL-Pi](https://github.com/NVlabs/SoL-Pi) | 3,497 | TypeScript | MIT | `2195680` | 94 | 2.6 MB | token 经济与上下文压缩 harness |
| `AutoResearch-main/` | [EvoMap/AutoResearch](https://github.com/EvoMap/AutoResearch) | 3,149 | Python | Apache-2.0 | `21f5912` | 221 | 2.0 MB | 跨域 Idea + 多模型评审 + 负结果 |
| `Automated-AI-Web-Researcher-Ollama-main/` | [TheBlewish/Automated-AI-Web-Researcher-Ollama](https://github.com/TheBlewish/Automated-AI-Web-Researcher-Ollama) | 3,020 | Python | MIT | `f9bd9d7` | 12 | 0.1 MB | 本地 Ollama 调研最小实现 |
| `awesome-autoresearch-main/` | [webfuse-com/awesome-autoresearch](https://github.com/webfuse-com/awesome-autoresearch) | 2,570 | — | NOASSERTION（需核对） | `473fe70` | 4 | <0.1 MB | 生态地图（非系统） |
| `AutoSci-main/` | [DAIR-AutoResearch/AutoSci](https://github.com/DAIR-AutoResearch/AutoSci) | 1,706 | Python | MIT | `f5c2fe0` | 286 | 16.2 MB | wiki 中心记忆 + 全生命周期 |
| `RSI-Anything-main/` | [Gen-Verse/RSI-Anything](https://github.com/Gen-Verse/RSI-Anything) | 797 | HTML / Python | Apache-2.0 | `8ba44cd` | 573 | 18.2 MB | 世界模型预筛 + incumbent guard + 判定封存 + 多域任务保留 |
| `OpenRSI-Index-main/` | [OpenRSI-Foundation/OpenRSI-Index](https://github.com/OpenRSI-Foundation/OpenRSI-Index) | 248 | Python | Apache-2.0 | `c80c190` | 1,560 | 137.5 MB | 持久 Work + 一次性干净 Judge + 私有测试 |

> `AutoResearchClaw-main (1).zip` 与 `AutoResearchClaw-main.zip` 的 SHA-256 完全相同，已跳过，未重复解压。
> `OpenRSI-Index-main (1).zip` 与 `OpenRSI-Index-main.zip` 的 SHA-256 相同（`385b11e3…76d25`），同样跳过。
> 完整哈希、压缩包路径、文件数与许可证见 [`metadata.json`](metadata.json)。
> 本地快照合计 **11 个项目、8,870 个文件、约 361.3 MB**（OpenRSI 贡献 1,560 文件 / 137.5 MB；RSI-Anything 贡献 573 文件 / 18.2 MB）。
> 另有 **3 个策展技能快照**（2026-10-23）：`Scientific-Agent-Skills-curated/`、`Academic-Research-Skills-curated/`、`AI-Research-SKILLs-curated/`；仅 19 个源文件 / 579.4 KB（含 `CURATION.md` 与 `metadata.json` 共 25 文件 / 约 656 KB），**不计入**上句的 11 个完整快照。详见 §4.3。
> `RSI-Anything-main/` 由用户直接放入本地目录（无对应 ZIP 留在 `oss/`），commit 与元数据经 GitHub API 核对；详见 [`metadata.json`](metadata.json)。

---

## 2. 关键代码入口

| 项目 | 先看这些文件/目录 | 可复用机制 | 不直接复用 |
| --- | --- | --- | --- |
| AutoResearchClaw | `researchclaw/pipeline/`、`hitl/`、`literature/`、`memory/`、`assessor/`、`prompts.default.yaml`、`docs/debate_engine.md` | 阶段编排、HITL 分级、四层引文核验、跨 run 记忆、评审评分 | 全自主投稿叙事；英文/代码域假设 |
| autoresearch | `prepare.py`、`train.py`、`program.md` | 固定层/探索层/控制层分离；edit-run-keep 与回滚 | 只覆盖代码实验，不是完整科研流程 |
| ARIS | `skills/research-lit/`、`idea-creator/`、`experiment-plan/`、`paper-figure/`、`citation-audit/`、`paper-claim-audit/`、`rebuttal/`、`research-wiki/` | 技能契约、文献综述、图表规范、引用审计、跨模型对抗评审 | 技能包强依赖；未核验的效果数字 |
| Auto-Empirical-Research-Skills | `catalog/skills.json`、`aers_score/`、`benchmark/`、`agents/` | 技能卡组织、统一 rubric/scorer、实证复现实验 | 只面向社科实证；不等于通用科研 |
| SoL-Pi | `src/sol-pi/`、`docs/compatibility.md`、`tests/` | token 预算、上下文压缩、证据保留 reducer、Action Fusion | 把成本下降当作科学正确性 |
| AutoResearch (EvoMap) | `idea_generation.py`、`check_idea.py`、`ar-runtime/`、`knowledge_base/`、`docs/` | 跨域 Idea、多模型评审、pilot-before-scaling、负结果保留 | 未核验的跨域效果声明 |
| Automated-AI-Web-Researcher-Ollama | `Web-LLM.py`、`research_manager.py`、`Self_Improving_Search.py`、`llm_wrapper.py` | L1 级调研基线；本地/离线、零 API 成本 | 无证据核验、无实验执行 |
| awesome-autoresearch | `README.md` | 生态地图与项目演化脉络 | 不是系统，不能作为能力基线 |
| AutoSci | `runtime/schema/`、`runtime/templates/`、`app/modules/graph.js`、`tools/`、`mcp-servers/` | wiki 中心记忆、schema/template、依赖图、自演化 | 记忆无准入门槛；自动科研宣称 |
| RSI-Anything | `src/rsi_anything/workflow/runner.py`、`config.py`、`tests/test_workflow.py`、`src/rsi_anything/tasks/code_repair.py`、`tasks/code_repair/src/development.py`、`tasks/code_repair/src/evaluation.py`、`tasks/gui/src/rsi_anything_gui/rsi.py`、`audit.py`、`protocol.py`、`experiment.py`、`tasks/gui/docs/PROTOCOL.md` | run/source identity、stage receipt、attempts 归档、resume/lock；世界模型预筛、incumbent guard、public seal、cohort 隔离、2×2 交叉、conditional confirmation、独立 raw-data audit、相对 incumbent 成本 | 保留对象是 checkpoint/pair；无租约/护照/撤销传播/claim 级证据闭合；五域公开代码不对称；作者数字未复现 |
| OpenRSI-Index | `RSI-Harness/README.md`、`RSI-Harness/docs/harbor-task-authoring/task-toml.md`、`rsi-tasks/depth-width-allocation/`、`checks/`、`CONTRIBUTING.md` | 持久 Work + 一次性干净 Judge、快照、私有测试、oracle、best-of-N、失败状态机、静态检查 | 8×H100/13 小时级任务负载；不写论文；不评中文写作 |

---

## 3. 能力覆盖矩阵（判断）

> ● 强；◐ 中/部分；○ 弱/无；— 不适用。基于仓库结构、技能文档与关键代码判断，**未运行、未复现**。● 只表示“仓库中存在可核对的强机制”，不表示端到端可运行或效果已验证。

| 项目 | 文献 | Idea 发散 | Idea 收敛 | 实验设计/执行 | 写作 | 绘图 | 评审/返修 | 记忆/技能 | 证据/审计 | 中文长文 | 失效追踪 |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| AutoResearchClaw | ● | ◐ | ◐ | ● | ● | ◐ | ◐ | ● | ● | ○ | ○ |
| autoresearch | ○ | ○ | ○ | ● | ○ | ○ | ○ | ○ | ◐ | ○ | ○ |
| ARIS | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | ◐ | ◐ |
| Auto-Empirical | ◐ | ◐ | ○ | ● | ● | ◐ | ◐ | ● | ● | ◐ | ○ |
| SoL-Pi | ○ | ○ | ○ | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ |
| AutoResearch (EvoMap) | ◐ | ● | ◐ | ◐ | ◐ | ○ | ◐ | ◐ | ◐ | ○ | ○ |
| Automated-AI-Web-Researcher | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| awesome-autoresearch | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| AutoSci | ◐ | ◐ | ◐ | ◐ | ◐ | ○ | ◐ | ● | ◐ | ○ | ◐ |
| RSI-Anything | ○ | ○ | ◐ | ● | ○ | ○ | ◐ | ◐ | ● | ○ | ○ |
| OpenRSI-Index | ○ | ○ | ○ | ● | ○ | ○ | ◐ | ○ | ● | ○ | ○ |
| **Research Agent（目标态）** | **●** | **●** | **●** | **●**（干实验；湿实验 P2） | **●** | **●** | **●**（P1） | **●** | **●** | **●** | **●** |

**三处修正**（优先于旧版判断，均可在代码中核对）：

- **ARIS 中文长文 `○ → ◐`**：有 NSFC 中文基金申请书（`skills/grant-proposal/SKILL.md`），但没有中文核刊全稿流程；**失效追踪 `○ → ◐`**：`paper-claim-audit` 会重算输入 SHA256 并标 `STALE`，但这是一次性审计，不是下游传播。
- **Auto-Empirical 中文长文 `○ → ◐`**：有中文学位论文 LaTeX 与 GB 标准（`skills/35-bahayonghang-academic-writing-skills/skills/latex-thesis-zh/`），也有通用中文论文写作技能（`skills/24-Imbad0202-academic-research-skills/academic-paper/`，繁中 IMRaD、APA 7.0）；但它是通用体裁，不是“证据槽 + 版面锚点”的中文核刊全流程，账本仍是手工 CSV。
- **AutoSci 失效追踪 `○ → ◐`**：`runtime/schema/edges.yaml` 定义了 `invalidates` 边；但代码中它只用于 dashboard 成熟度判断，未见向稿件/claim 的传播。

**RSI-Anything 的定位**：它的“实验设计/执行”和“证据/审计”是**任务层**的强机制，而且比上一版判断更完整：除 world model 预筛、incumbent guard、public seal、cohort 隔离外，还有 **run/source identity、stage receipt、attempts 归档、2×2 交叉（old_old/old_new/new_old/new_new）、conditional confirmation、独立 raw-data audit**。但“记忆/技能”只到 checkpoint/pair retain，没有租约、适用域护照与撤销传播；“评审/返修”是任务判定，不是中文稿件评审；“失效追踪”无 claim→句/图传播。因此其“证据/审计 ●”只表示运行级审计强，不表示稿件证据闭合。逐项代码入口与四种 retain 的不对称见 `12-` §2–§3。

**四种 retain 要分开读**：代码修复是四段 checkpoint 链；GUI 是两代 `world+policy+controller` pair + 2×2 交叉；实验室规划的公开代码只到冻结推理；反应优化的预测在循环中保持冻结、没有模型更新；免疫科学未发布。不能按 README 的“五域”等权计分，也不能把 reaction optimization 叫 RSI。详见 `12-` §2.3。

**矩阵读法**：开源在单点能力上已经很强（ARIS 的技能与审计、AutoResearchClaw 的阶段契约、Auto-Empirical 的评分、AutoSci 的记忆与图 schema、RSI-Anything 的世界模型预筛与 incumbent guard），但**本轮快照中没有一家把“句子级证据槽 + 跨版本失效传播 + 中文核刊证据链”同时做成主路径**。这才是 `02-` §4.2 的差异所在，而不是“开源都没做”。

### 3.1 执行验证能力（OpenRSI / PaperBenchX）

主矩阵的“实验设计/执行”一列看不出判定质量，单列一张表。PaperBenchX 无本地代码，只按项目口径列出。

| 能力 | OpenRSI-Index | PaperBenchX（项目口径） | Research Agent RWVH（设计） |
| --- | :-: | :-: | :-: |
| 持久 Work + 提交快照 | ● | ◐（隔离重跑） | ● |
| 一次性干净 Judge / 只读挂载 | ● | ● | ● |
| 私有测试 / 私有 rubric | ● | ● | ● |
| oracle / nop 校准 | ●（oracle） | ◐（success/partial/invalid） | ●（oracle + nop） |
| best-of-N 有效提交 | ● | ◐ | ●（仅 `scored`） |
| 失败状态机（infra ≠ 0） | ● | ◐ | ● |
| 独立无网重跑 | ● | ● | ●（v1 允许本地缓存镜像） |
| 三阶段复现评分 | ○（任务自定义 reward） | ●（M/E/V） | ●（R = 0.30/0.30/0.40） |
| 结果 claim → 稿件槽 | ○ | ○ | ● |
| 中文核刊写作审计 | ○ | ○ | ● |
| RWJT 联合任务 | ○ | ○ | ● |
| 单任务成本 | 高（最高 8×H100 / 13 h） | 高（93 任务 / 10 原生环境） | CPU/单卡，Judge ≤ 30 min，≤ 50 元 |

**结论**：OpenRSI 与 PaperBenchX 把“执行可信”做成了可工程化判定，但没有把判定结果接到中文长文的句子上；RWVH 借其隔离、重跑、私有 rubric 与失败状态机，增量做 **`EA` 绑定、导出硬门与 RWJT**。逐项事实与入口见 `07-` §1 与 `03-` §2.5–§2.6。

---

## 4. 相对这些代码，我们的差异

### 4.1 开源已实现，不能再宣称“首创”

| 能力 | 代码证据 | 正确表述 |
| --- | --- | --- |
| 中文基金申请书 | ARIS `skills/grant-proposal/SKILL.md`（NSFC，中文） | 不说“首个中文申报书生成”；差异在证据绑定与失效传播 |
| 数字 / claim 审计 | ARIS `paper-claim-audit`；AutoResearchClaw `pipeline/paper_verifier.py`；Auto-Empirical `aer-consistency` | 不说“首创数字核验”；差异在生成时槽位绑定与跨版本传播 |
| Claim 驱动实验设计 | ARIS `skills/experiment-plan/SKILL.md`、`result-to-claim` | 不说“首创 claim→实验”；差异在设计卡冻结、基线复现、全局隔离 |
| 图谱失效边 | AutoSci `runtime/schema/edges.yaml` 的 `invalidates` | 不说“首创失效边”；差异在传播语义与稿件句联动 |
| 盲审 / 自评校准 | EvoMap `ar-runtime/.claude/agents/ar-blind-reviewer.md`（`calibration_gap`） | 不说“首创盲审”；差异在 claim / artifact 级评审绑定 |
| 哈希收据 / 裁决完整性 | EvoMap `ar-runtime/scripts/ar-workflow-engine.py` | 不说“首创收据”；差异在 claim 级依赖闭包 |
| 中文论文 / 学位论文写作 | Auto-Empirical `academic-paper`（繁中 IMRaD、APA 7.0）、`latex-thesis-zh` + `GB_STANDARD.md`；ARIS NSFC 申请书 | 不说“首个中文长文”；差异在中文核刊证据槽与版面锚点 |
| 探索 / 确证隔离 | AutoSci `hiera-experiment`（探索侧车不写 wiki、不转正式 claim） | 不说“首创隔离”；差异在全局执行策略与运行时强制 |
| 持久 Work + 一次性 Judge | OpenRSI `RSI-Harness/README.md`（Work 暂停快照 → 干净 Judge 只读挂载 → 私有测试 → reward） | 不说“首创 Work/Judge”；差异在把判定接到中文稿件槽与导出 |
| 干净重跑 / 只认重跑产物 | OpenRSI `clean_image`、Judge 重训；PaperBenchX 独立无网重跑（项目口径） | 不说“首创独立重跑”；差异在 RWJT 与 `EA` 生命周期 |
| oracle / nop / best-of-N | OpenRSI `--agent oracle`、提交状态机与 best reward | 不说“首创 oracle”；差异在 oracle+nop 双校准与写作分联合 |
| 私有 rubric / 三阶段复现评分 | OpenRSI 私有测试 + task reward；PaperBenchX Modeling/Execution/Validation rubric | 不说“首创三阶段”；差异在 R/W 联合与中文写作审计 |
| 开放/封闭集 + canary | OpenRSI `checks/`（canary、隐藏测试、发布扫描）；PaperBenchX 12 开放 / 81 封闭 | 不说“首创污染控制”；canary 只用于 benchmark 污染控制，不用于规避 AIGC 检测 |
| 阶段产物契约 | AutoResearchClaw `pipeline/contracts.py` + `executor.py`（输入/输出运行时检查） | 不说“首创产物契约”；差异在契约粒度下推到 claim/句/槽 |
| 预测预筛 / incumbent 保护 | RSI-Anything `tasks/code_repair/src/development.py`（预测 utility；未超过 incumbent 则保留）、世界模型 JEPA-Anything | 不说“首创预测预筛/incumbent”；差异在把 guard 接到 claim 级租约与撤销传播 |
| 判定封存 / cohort 隔离 | RSI-Anything `tasks/code_repair/src/evaluation.py`（`public_seal.json`、`all_decisions_sealed_before_hidden_judge`）、`tasks/gui/docs/PROTOCOL.md`（互斥 cohort seeds） | 不说“首创封存/隔离”；差异在封存对象是候选+四问判据+稿件槽，且导出 fail-closed |
| 2×2 交叉 / conditional confirmation | RSI-Anything `tasks/gui/src/rsi_anything_gui/rsi.py`（两代 pair 冻结后 old/new × old/new 交叉）、`protocol.py`（pilot gain ≥0.05 才开 confirmation；`limits` 明确一个 DOM 模板/一个 seed） | 不说“首创交叉/确认”；差异在把归因下推到 claim 级资产与稿件槽，并把阈值写成带来源的 scope 配置 |
| 独立 raw-data 审计 | RSI-Anything `tasks/gui/src/rsi_anything_gui/audit.py`（从 raw transitions 重算动作、episode 链、训练谱系、校准、冻结时间、成本、promotion） | 不说“首创独立审计”；差异在审计对象是 asset→run→claim→句/图与导出硬门 |

### 4.2 仍然成立的差异（每条都要有验收）

1. **句子级证据槽 + 导出硬门**：不是“有 claims-evidence matrix”，而是每个事实句、数字、图表都有可解析槽位；未解析槽位阻止导出。开源多为 section 级矩阵（AutoSci）、计划级矩阵（ARIS）或事后审计（Auto-Empirical）。
2. **跨版本失效传播**：数据/代码/图表变更后，沿 `depends_on` / `derived_from` / `supports` 计算受影响 claim 与稿件句，并给出“重跑 / 重写 / 复核”处置。AutoSci 有边类型但无传播；ARIS 只有一次性 `STALE`；Auto-Empirical 靠手工改 CSV。
3. **统一 claim 类型系统**：`literature_claim` / `result_claim` / `manuscript_claim` 共用 ID 空间与 schema，冲突证据可定位到同一 ID。开源分别管文献卡、实验数值与稿件矩阵，三套对象未合并。
4. **中文核刊体裁 + 中文版面锚点**：章节义务、结构化摘要、GB/T 7714、中文 PDF 的“页—段—句”锚定。ARIS 有 NSFC 申请书，Auto-Empirical 有通用中文论文/学位论文写作，但都不是“claim 槽 + 版面锚定”的中文核刊全流程。
5. **过程指标的预注册评测**：Q0 通过率、claim 支持率、失效召回、人工干预次数、体裁合规五项，报告负结果；不以单一 AI 评审分作质量结论。开源有评分器与盲审，但多为终稿分数。
6. **技能准入与负迁移控制**：技能/记忆先在小样本上测迁移、保留、退化与成本，再决定是否进入主路径。RSI-Anything 已有任务级 promotion gate（增益 + 相对 incumbent 成本）、incumbent guard、2×2 交叉与 conditional confirmation；我们补的是 **claim 级租约、适用域护照、撤销传播与“P8 只产候选”**。ARIS 与 Auto-Empirical 有大规模技能库，但本轮未检索到统一的“何时可复用、何时拒绝”准入测试；AutoSci 的 SciEvolve 在本快照 README 中指向 `paper` 分支，未含实现。
7. **可审计导出包**：稿件、证据图谱、设计卡、图表代码、运行记录、AI 使用记录一起交付，而不是只给 PDF。EvoMap 有裁决收据、AutoResearchClaw 有 run 目录，但未见面向中文长文的统一交付清单。
8. **RWJT 复现—写作联合任务**：先复现结果，再写成中文核刊段落；J = 0.55 R + 0.45 W；计分数字必须绑 `EA(source=rerun)`，伪造直接 invalid。OpenRSI 停在运行产物与 reward，PaperBenchX 停在复现 rubric 分；本轮快照与公开材料中未见把“干净重跑 → result_claim → 中文句子/数字/图槽 → 导出硬门”接成一条链的实现。**这是 D8，也是最值得作为方法论文投稿的一条。**

### 4.3 策展技能快照（2026-10-23）

> 不是完整仓库：只保留 README、LICENSE 与代表性 `SKILL.md`，用来看“技能如何声明、如何加载、如何写检查点”，不运行、不复现效果。完整目录与安装方式见上游 README；每个目录的 `metadata.json` 记录 commit、文件大小与省略范围。

| 目录 | 仓库 | Commit | 许可证 | 源文件 | 体积 | 选了什么 |
| --- | --- | --- | --- | ---: | ---: | --- |
| `Scientific-Agent-Skills-curated/` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | `593377b` | MIT | 7 | 161.9 KB | literature-review、scientific-writing、statistical-analysis、scanpy、rdkit |
| `Academic-Research-Skills-curated/` | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | `3224a27` | **CC BY-NC 4.0** | 6 | 280.7 KB | academic-pipeline、academic-paper、academic-paper-reviewer、deep-research |
| `AI-Research-SKILLs-curated/` | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | `773a529` | MIT | 6 | 136.8 KB | autoresearch、lm-evaluation-harness、ml-paper-writing、rigor-reviewer |

共 **19 个源文件 / 579.4 KB**。K-Dense 完整 ZIP 约 235 MB，直连 `github.com` 在当前环境被重置；因此改用 GitHub Contents API 按文件下载，并保留 commit 便于复核。

**逐项读到的机制**：

- **K-Dense `scientific-writing`**：把“不编造、证据绑定、人类 verifier 记录、保密、科学保真”写成不可协商规则；单列 `Verification scope` 说明本技能不验证什么。比“写作时加引用”强，说明我们的 skill manifest 需要 `evidence_contract` 与 `verification_scope`。
- **K-Dense `literature-review`**：7 阶段（planning → search → screening → extraction → synthesis → citation verification → document generation），记录 query/date、PRISMA records/reports/studies 分层、排除理由；明确指出 DOI 存在不等于 claim 支持。对应我们 P1 还缺的“检索日期 + 覆盖回执 + 排除理由”。
- **Academic Research Skills `academic-pipeline`**：10 阶段 + 状态机 + FULL/SLIM/MANDATORY 检查点 + integrity/re-review/re-revise + process summary。它仍是固定 pipeline；我们借它的**强制检查点/状态机纪律**，不照搬其阶段顺序。
- **AI-Research-SKILLs `autoresearch`**：two-loop 明确是“节奏，不是铁路”，可回到文献、改问题、pivot；实验前把 protocol commit 到 git，形成“计划先于结果”的时间证明；`research-state.yaml`/`findings.md` 记录状态与发现；按领域路由 skill。对应我们的 RunCapsule 应补 `protocol_hash` 与 findings/run-state。
- **`rigor-reviewer`**：六维语义评审（evidence relevance、falsifiability、scope calibration、argument coherence、exploration integrity、methodological rigor）；可作为我们的“论证完整性”建议轴，但不能替代结构闭合的阻断轴。

**许可证纪律**：`Academic-Research-Skills-curated` 是 **CC BY-NC 4.0**，只用于非商业阅读/对照，不得直接并入产品交付物；K-Dense 与 AI-Research-SKILLs 为 MIT，复用代码/文档前仍需逐文件核对许可证与署名。详见 [`../16-科研Skill生态调研与动态流程编排.md`](../16-科研Skill生态调研与动态流程编排.md) §2.1、§5.5。

### 4.4 对外表述纪律

- 写“在开源单点机制之上做统一契约层”，不写“全面超越”或“开源都没做”。
- 任何“提升 / 更快 / 更准”必须来自本地同协议对照；未复现前只写机制，不写效果数字。
- 复用开源组件需逐项核对许可证，并在交付物中注明来源与版本。

逐项代码入口与审计记录见 [`../03-调研留痕-市场竞品与研究依据.md`](../03-调研留痕-市场竞品与研究依据.md) §2.5；需求书中的对应章节见 [`../02-需求书-科研自动化与写作平台.md`](../02-需求书-科研自动化与写作平台.md) §4.2。

---

## 5. 使用与更新

### 5.1 完整 clone：`oss/full/`（2026-10-23 增补）

`oss/*-main/` 是**工作树快照**（来自 ZIP，通常没有 `.git`）；`oss/full/` 放**完整 git clone**（保留 `.git`）或明确标注的完整工作树快照/中断副本。三者不能混写。

- 保留完整 `.git` 历史（不使用 `--depth`/`--filter`）、递归子模块和 LFS 对象；
- 独立目录，不与上面的 11 个快照混在一起；不计入快照文件数/体积；
- 只用于本地研究/对照，**不提交、不再分发**；`oss/full/` 已加入 `.gitignore`；
- 每个仓库的 clone 类型、commit、branch、许可证、体积、LFS/子模块状态、中断记录见 [`full/CLONES.md`](full/CLONES.md)；
- 截至 2026-10-23：4 个完整 git clone（SciToolAgent、DeepScientist、CycleResearcher、AI-Scientist-v3）+ 10 个完整工作树快照；`HKUDS/AI-Researcher` 因工作树 901 MB（大量 examples GIF/数据集）暂停在 263 MB，标为 `partial`；
- 未完成/失败的 clone 标 `partial/pending`，不能当作完整仓库；ZIP 快照没有 `.git`，不能写成“完整 clone”；
- 许可证风险：`AI-Researcher` 仓库页未声明许可证，`InternAgent` 为 `NOASSERTION`，`CycleResearcher` 为研究专用的 *CycleResearcher License*（非 OSI，**不复用/不打包/不再分发**），`DeepScientist`/`AI-Scientist-v3` 为 Apache-2.0，`SciToolAgent` 为 MIT；复用代码前逐文件核对，不能直接打包进产品。

复现命令：`bash scripts/clone-research-repos.sh`。该脚本会在 `oss/full/` 下按完整 clone 方式拉取核心自改进 + 浙大 + 代表性框架，并把日志写到 `oss/full/clone.log`。完整 clone 体积较大（数百 MB 到 GB），网络慢时请分批执行；不要用浅拷贝冒充“完整”。

- 本目录是**参考快照**，不是产品依赖；不要把外部代码直接打包进交付物，复用前逐项核对许可证。
- 只借机制与接口，不借外部项目的效果数字；所有"有效/提升"声明必须在本地重测后再写入对外材料。
- 更新方式：重新下载对应仓库的 ZIP，覆盖同名目录，更新 `metadata.json` 中的 commit、日期与 SHA-256；不要只改 README 表。
- 未纳入本轮快照：ToolUniverse、OpenScholar、PaperQA2、SciArena、AutoSDT-5K、SciNet。它们仍在 `00-`/`03-` 的文献清单中，需要时再单独拉取。

### 5.2 写作 skill 完整仓库：`oss/writing-skills/`（2026-10-23 增补）

为 `WritingProfile`（中文期刊 / 英文会议 / 学位论文 / 基金）提供完整仓库底本，**不是 curated 摘录**：

- 9 个仓库均为 `git-full`（`.git` 完整、`is-shallow-repository=false`）：zLanqing、Master-cai、SNL-UCSB、lishix520、LeonChaoX/qinyan、JingYangYuan、Tianyuai/SCUT、Orchestra-Research/AI-Research-SKILLs、Imbad0202/academic-research-skills；
- 逐仓 commit、许可证、skill 数与关键 skill 见 [`writing-skills/CLONES.md`](writing-skills/CLONES.md)；
- 8 个 MIT；`Imbad0202/academic-research-skills` 是 **CC BY-NC 4.0**，只读对照、不进产品；
- 不纳入 `academic-humanizer`、`AIGC-Detector-Rewriter`、`humanize-mba-text` 等以规避 AIGC 检测为目的的仓库；
- 本目录本地只读，根 `.gitignore` 仅保留 `CLONES.md`，不随站点发布。

复现命令：`python scripts/fetch-writing-skills.py`。

---

## 6. 关联文档

- [`../04-自动化研究与写作流水线.md`](../04-自动化研究与写作流水线.md) §4：开源复用映射；§2.14.1：RWVH 接入。
- [`../05-全流程设计与Co-Scientist对照.md`](../05-全流程设计与Co-Scientist对照.md) §1.7：OpenRSI/PaperBenchX 执行验证；§3：全流程能力矩阵；§5.3：采纳/改造/拒绝。
- [`../07-复现级验证与执行Harness设计.md`](../07-复现级验证与执行Harness设计.md)：RWVH 设计、X0–X7、R/W/J、任务包与 FR-18–FR-24。
- [`../02-需求书-科研自动化与写作平台.md`](../02-需求书-科研自动化与写作平台.md) §4.2：与本地开源快照的逐项对比；§4.2.4：三条路线、D1–D8 与 190 人周基线对账；§4.2.5–§4.2.6：复现级验证层与 215/229 人周重算；§5：功能需求。
- [`../03-调研留痕-市场竞品与研究依据.md`](../03-调研留痕-市场竞品与研究依据.md) §2.3–§2.6：研究证据、竞品快照、开源逐项审计与 PaperBenchX 外部参照。

---

*快照仅用于研究与对比，不构成对任何项目效果的背书。*
