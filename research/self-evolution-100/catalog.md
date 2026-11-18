# 自进化 / RSI 百篇目录（2022–2026）

快照：2026-10-24 · 来源：arXiv API · 100/1207 筛选 · 元数据逐条核验，摘要级阅读；未复现任何论文。

## A 基础机制（22 篇）

| # | 论文 | 年份 / ID | 优化对象 | 反馈信号 | 读点与边界 | 与本仓库的关系 |
|---|---|---|---|---|---|---|
| 1 | STaR: Bootstrapping Reasoning With Reasoning | 2022 / [2203.14465](https://arxiv.org/abs/2203.14465) | 推理轨迹/策略 | 答案正确性过滤 | 用自生成 rationale 回灌训练；只保留正确答案，属于'有标签的自举'。边界是标签与分布，不是开放式自我改进。 | 对应我们 S2–S3 的候选假设生成：可借'生成→筛选'，但不能把模型自评当 G1。 |
| 2 | Self-Refine: Iterative Refinement with Self-Feedback | 2023 / [2303.17651](https://arxiv.org/abs/2303.17651) | 输出/推理步骤 | 同一模型自反馈 | 同模型 critique-revise 迭代；无需训练，但反馈信号与生成器同源，容易在无外部验证时平台化。 | 我们 paper 模块的 self-check 只能做风格/槽位检查，不能替代 Q1/G4。 |
| 3 | Reflexion: Language Agents with Verbal Reinforcement Learning | 2023 / [2303.11366](https://arxiv.org/abs/2303.11366) | 行为策略/记忆 | 环境反馈 + 语言反思 | 把失败轨迹写成反思存入 episodic memory，下一轮条件化；不改权重。关键在反馈是否可验证。 | 与 ProcessProtocol 最接近；但 Reflexion 没有 lease、scope 与撤销，我们要补治理。 |
| 4 | Self-Rewarding Language Models | 2024 / [2401.10020](https://arxiv.org/abs/2401.10020) | 策略/奖励模型 | 模型自当 judge | 用模型自身给回复打分并迭代训练；展示了自奖励可行，也暴露自评偏差与 reward hacking。 | 我们明确禁止自评生成 claim；可作为'为什么需要外部 evaluator'的反例。 |
| 5 | Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models | 2024 / [2401.01335](https://arxiv.org/abs/2401.01335) | 策略 | 人类偏好数据 + 自博弈 | 让弱模型与历史版本自博弈，理论上有偏好优化解释；仍需人类偏好种子。 | 说明'零外部信号'不成立；我们的 S1 真实语料也是外部 grounding。 |
| 6 | Absolute Zero: Reinforced Self-play Reasoning with Zero Data | 2025 / [2505.03335](https://arxiv.org/abs/2505.03335) | 策略/任务生成 | 可验证 reward（代码/数学） | 模型自己出题、自己解题，用执行器验证；零人类数据但依赖强 verifier 域。 | 对应我们 S5 的 run/EA：只有可执行验证的域才适合闭环；科研主张没有这么干净的 verifier。 |
| 7 | R-Zero: Self-Evolving Reasoning LLM from Zero Data | 2025 / [2508.05004](https://arxiv.org/abs/2508.05004) | 策略（challenger/solver） | 可验证答案 |  challenger 生成难度适配的问题，solver 求解，共同进化；解决 zero-data 冷启动，但分布会漂移。 | 我们 S5 的 seed-budget 只是超参选择，不是 challenger/solver 共同进化。 |
| 8 | Self-Adapting Language Models | 2025 / [2506.10943](https://arxiv.org/abs/2506.10943) | 模型权重 | 自生成训练数据 + SFT | 模型生成 self-edit（含训练数据与超参），再用 RL/SFT 更新权重；会遗忘、需奖励设计。 | 我们是 frozen backbone + 改 harness，明确不训练；SEAL 只作对照。 |
| 9 | Transformer-Squared: Self-adaptive LLMs | 2025 / [2501.06252](https://arxiv.org/abs/2501.06252) | 模型权重/任务向量 | RL 自适配 | 用任务向量组合实现 test-time self-adaptation；比全量微调轻，但仍改权重。 | 我们的允许面是 skill/process/prompt/knowledge，不含权重。 |
| 10 | Learning to (Learn at Test Time): RNNs with Expressive Hidden States | 2024 / [2407.04620](https://arxiv.org/abs/2407.04620) | 隐藏状态/权重 | 自监督 next-token | TTT 在测试时用自监督更新内部状态；不是 agent harness 级自我改进。 | 提醒我们'test-time learning'与'harness RSI'是不同层，不能混写。 |
| 11 | Titans: Learning to Memorize at Test Time | 2024 / [2501.00663](https://arxiv.org/abs/2501.00663) | 神经记忆 | 长上下文预测 | Titans 用可学习记忆模块处理超长上下文；是记忆架构，不是自进化治理。 | 我们的 memory 候选需要版本/租约，Titans 不提供治理。 |
| 12 | Large Language Models as Optimizers | 2023 / [2309.03409](https://arxiv.org/abs/2309.03409) | prompt | 任务分数 | LLM 作为优化器迭代 prompt；搜索空间大、评估成本高，缺少 archive。 | 对应 GEPA/ACE 的前身；我们 literature 的 query plan 也可做小规模 prompt 搜索，但必须有 held-out。 |
| 13 | Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution | 2023 / [2309.16797](https://arxiv.org/abs/2309.16797) | prompt/变异算子 | 任务适应度 | 自指 prompt 进化，连变异 prompt 也进化；易过拟合 benchmark。 | 提示我们 candidate patch 需要限制编辑预算，不能无限叠加。 |
| 14 | TextGrad: Automatic "Differentiation" via Text | 2024 / [2406.07496](https://arxiv.org/abs/2406.07496) | 文本变量/代码 | 任务损失（文本梯度） | 把自然语言反馈当梯度优化 prompt/code；通用但依赖评估器质量。 | 可用于 S8 写作修订，但不能让文本梯度直接改 claim。 |
| 15 | DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines | 2023 / [2310.03714](https://arxiv.org/abs/2310.03714) | pipeline/prompt | metric + optimizer | 声明式 LM 程序 + 编译器/优化器；把 prompt 当可优化参数，适合固定任务。 | 我们的 SPEC/artifact 编排更像 DSPy 的契约层；可借'编译'思想做 harness 版本。 |
| 16 | GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning | 2025 / [2507.19457](https://arxiv.org/abs/2507.19457) | prompt/程序 | 任务 reward + 反思 | 反思式 prompt 进化，Pareto 选择；少量 rollout 即可超过 RL，但仍是单任务优化。 | 对应我们 rsi_fixture 的候选选择；我们缺少 Pareto 与多目标。 |
| 17 | Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models | 2025 / [2510.04618](https://arxiv.org/abs/2510.04618) | 上下文/playbook | 任务反馈 + 自编辑 | 让 context 成为可 grow-and-refine 的 playbook，抑制 brevity bias/context collapse；不训练。 | 与我们的 knowledge/process 候选最接近；但 ACE 的自编辑需要外部验证，否则会积累错误。 |
| 18 | Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation | 2023 / [2310.02304](https://arxiv.org/abs/2310.02304) | 代码（scaffold） | 下游任务分数 | 让模型改写自己的 scaffold，递归自我改进；在小任务上有效，但会 reward hack。 | 我们 rsi 的 target 禁改 claim/gate，但 patch 仍是自由文本；STOP 是反例。 |
| 19 | AlphaEvolve: A coding agent for scientific and algorithmic discovery | 2025 / [2506.13131](https://arxiv.org/abs/2506.13131) | 算法代码 | 自动评估器 | 进化式代码搜索，评估器可验证；在数学/系统优化上有真实发现，但算力巨大且域受限。 | 对应我们 figure/algorithm 类候选；没有可执行 evaluator 的科研阶段不能照搬。 |
| 20 | A Self-Improving Coding Agent | 2025 / [2504.15228](https://arxiv.org/abs/2504.15228) | 自身代码 | benchmark 分数 | coding agent 直接编辑自身代码并保留有效修改；单域、单 benchmark，缺少跨域治理。 | 我们的 S1/S5 harness 改进是其受治理版本；但只消费两个 target，远未覆盖。 |
| 21 | Gödel Agent: A Self-Referential Agent Framework for Recursive Self-Improvement | 2024 / [2410.04444](https://arxiv.org/abs/2410.04444) | 自身代码/策略 | 任务反馈 | 运行时自指修改逻辑；开放度高、可解释性/安全性弱。 | 我们明确不允许无约束自改；Gödel Agent 是'为什么需要 lease'的对照。 |
| 22 | AgentEvolver: Towards Efficient Self-Evolving Agent System | 2025 / [2511.10395](https://arxiv.org/abs/2511.10395) | agent 策略/数据 | 环境反馈 + RL | 自提问、自导航、自归因的经验收集与训练；偏训练型，不是纯 harness。 | 我们的 frozen-model 路线不采用其训练部分，只借'经验归因'字段。 |

## B 自改与进化（20 篇）

| # | 论文 | 年份 / ID | 优化对象 | 反馈信号 | 读点与边界 | 与本仓库的关系 |
|---|---|---|---|---|---|---|
| 23 | Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents | 2025 / [2505.22954](https://arxiv.org/abs/2505.22954) | agent 代码/archive | benchmark + 安全沙箱 | archive 保留多样父代，自我修改在沙箱内评测；开放-ended，但依赖 benchmark 与沙箱。 | 我们 rsi.py 的 archive/select_parents 直接借自 DGM，但选择分数只是 hidden 指标均值。 |
| 24 | Huxley-Gödel Machine: Human-Level Coding Agent Development by an Approximation of the Optimal Self-Improving Machine | 2025 / [2510.21614](https://arxiv.org/abs/2510.21614) | agent 代码树 | benchmark + 元学习 | 用树搜索近似最优自改进机器，强调 metaproductivity 而非单点分数；计算昂贵。 | 提醒我们'当前分数'不等于'改进能力'；MetaTracker 应记录后者。 |
| 25 | Self Improvement via Fast Tree-search | 2026 / [2609.19526](https://arxiv.org/abs/2609.19526) | 自身代码/patch | 成对 judge + 下游任务 | 用 LLM pairwise judge + 正则 Bradley-Terry 指导树搜索，把昂贵下游评测留给最有希望的节点。 | 可补我们缺少的 judge 预筛；但 judge 偏差必须用 sealed 任务校准。 |
| 26 | Automated Design of Agentic Systems | 2024 / [2408.08435](https://arxiv.org/abs/2408.08435) | agent 架构 | 任务分数 + archive | meta-agent 搜索 agent 设计空间；在固定 benchmark 上有效，跨域迁移弱。 | 对应我们 rsi_fixture 的候选 agent/流程；我们只做检索预算，复杂度低。 |
| 27 | Voyager: An Open-Ended Embodied Agent with Large Language Models | 2023 / [2305.16291](https://arxiv.org/abs/2305.16291) | 技能库 | 环境奖励 + 课程 | Minecraft 中的自动课程 + 可复用技能库；技能是代码，不是自然语言记忆。 | 我们的 skill/process 候选应区分代码技能与文本协议。 |
| 28 | ExpeL: LLM Agents Are Experiential Learners | 2023 / [2308.10144](https://arxiv.org/abs/2308.10144) | 经验记忆 | 任务成功/失败 | 从跨任务轨迹提取 insight，推理时检索；不改权重。 | 与 our knowledge 候选相近；需要 provenance 与失效条件。 |
| 29 | Agent Workflow Memory | 2024 / [2409.07429](https://arxiv.org/abs/2409.07429) | workflow 记忆 | 任务成功率 | 从轨迹归纳可复用 workflow，检索后条件化；web agent 场景。 | 可映射到 ProcessProtocol；我们尚未有真实 workflow loader。 |
| 30 | ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory | 2025 / [2509.25140](https://arxiv.org/abs/2509.25140) | 推理记忆 | 任务反馈 + 检索 | 把成功/失败推理写成 memory，按任务检索；记忆质量决定上限。 | 我们 knowledge 候选若没有验证/去毒，会成为错误放大器。 |
| 31 | SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning | 2026 / [2602.08234](https://arxiv.org/abs/2602.08234) | 技能库/策略 | RL 奖励 | 递归技能增强 RL；训练 curator/executor，技能可组合。 | 训练型，只作对照；我们保持 frozen backbone。 |
| 32 | SkillOS: Learning Skill Curation for Self-Evolving Agents | 2026 / [2605.06614](https://arxiv.org/abs/2605.06614) | 技能库 curation | 延迟任务反馈 + RL | 冻结 executor + 可训练 curator，学习何时增删改技能；解决长程信用分配。 | 我们的 rsi 没有 curator，只有人工 propose；可借'技能操作类型'设计 schema。 |
| 33 | SKILLFOUNDRY: Building Self-Evolving Agent Skill Libraries from Heterogeneous Scientific Resources | 2026 / [2604.03964](https://arxiv.org/abs/2604.03964) | 科学技能库 | 领域资源 + 验证 | 把论文/API/notebook 编译成带 provenance、测试、环境假设的技能包，再闭环修剪。 | 与我们'科研 skill'方向最接近；我们的 modules/*/SPEC 可视为手写技能包。 |
| 34 | SEARL: Joint Optimization of Policy and Tool Graph Memory for Self-Evolving Agents | 2026 / [2604.07791](https://arxiv.org/abs/2604.07791) | 策略 + 工具图记忆 | 联合 RL | 联合优化 policy 与 tool graph memory；强调工具关系而非纯文本。 | 提醒我们 artifact 图也是可学习对象；当前 artifact store 未参与候选。 |
| 35 | R$^2$ Flow: Recursive Self-Improvement via Recursive Skill Evolution | 2026 / [2609.33867](https://arxiv.org/abs/2609.33867) | 技能库/策略 | 独立 verifier + signed utility | 交替策略学习、独立验证、版本化技能库更新；用 residual-variance plateau 决定何时更新。 | 直接可借：我们的 candidate 更新缺少'何时停止'与版本化 skill library。 |
| 36 | Metis: Bridging Text and Code Memory for Self-Evolving Agents | 2026 / [2606.24151](https://arxiv.org/abs/2606.24151) | 文本/代码记忆 | 任务反馈 | 桥接文本记忆与代码记忆，支持自进化 agent 的经验复用。 | 我们的 memory 候选目前只是概念，没有 text/code 双存储。 |
| 37 | Generalized Agent Iteration: One Formal Framework for Iterative Policy Improvement and Recursive Self-Improvement | 2026 / [2609.13406](https://arxiv.org/abs/2609.13406) | 形式框架 | 外部 grounding | GAI 用两个维度区分 GPI/RSI：改进机制是否属于 agent、评价标准是否外生。 | 这是定义我们系统的关键：改进机制在系统外（人+gate），评价标准外生，因此不是严格 RSI，而是受治理 harness 改进。 |
| 38 | Recursive Self-Evolving Agents via Held-Out Selection | 2026 / [2606.28374](https://arxiv.org/abs/2606.28374) | 自然语言 artifact | strict held-out keep-better | RSEA 维护 strategy/skills/playbook 三层状态，每代只在 disjoint held-out 不回归时提交；发现没有 universal winner。 | 直接命中我们的弱点：单一 hidden 集 + 一次选择；需要 held-out selection 与多 artifact 对照。 |
| 39 | DataFoundry: Evolving Data Preparators via Recursive Self-Improvement | 2026 / [2608.29966](https://arxiv.org/abs/2608.29966) | 数据准备器 | 领域 pilot + 诊断 | 把 data preparator 作为可演化 runtime spec，先在小 pilot 诊断再扩量；Skills-as-Modules。 | 我们 S1/S5 的 fixture/harness 也可视为 preparator；但缺少 pilot→scale 的预算门。 |
| 40 | MELD: Recursive Self-Improvement via Hierarchical Coordination for Multi-Agent Scientific Discovery | 2026 / [2610.24454](https://arxiv.org/abs/2610.24454) | 多 agent 团队策略 | GRPO + 共享预算 | Coordinator 与 Scientist 双层策略在 discovery tree 上共同进化；有 regret bound。 | 我们默认单 agent；MELD 说明多 agent 自进化的收益需要任务耦合，不应为'多'而多。 |
| 41 | EvoScientist: Towards Multi-Agent Evolving AI Scientists for End-to-End Scientific Discovery | 2026 / [2603.08127](https://arxiv.org/abs/2603.08127) | 科研 agent 团队 | 端到端 discovery | 多 agent  evolving AI scientist，覆盖 idea→实验→写作；效果依赖领域与工具。 | 我们的流程模块化更细，但缺真实 discovery 任务。 |
| 42 | SciToolAgent-Evo: An Ontology-Aware Self-Evolving Agent for Open-World Scientific Tool Acquisition | 2026 / [2607.28692](https://arxiv.org/abs/2607.28692) | 科学工具获取 |  ontology + 环境反馈 | 面向开放世界的科学工具获取与自进化；工具 schema/权限是关键。 | 对应我们 skill manifest 的 permissions/evidence_contract；目前只是文档字段。 |

## C 科研自动化（21 篇）

| # | 论文 | 年份 / ID | 优化对象 | 反馈信号 | 读点与边界 | 与本仓库的关系 |
|---|---|---|---|---|---|---|
| 43 | The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery | 2024 / [2408.06292](https://arxiv.org/abs/2408.06292) | 端到端论文 | 自动 reviewer + 人工 | 从 idea 到实验到论文的全自动流水线；实验多为计算型，审稿信号弱。 | 我们的 S1→paper 纵切在结构上相似，但没有真实 idea/实验搜索。 |
| 44 | The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search | 2025 / [2504.08066](https://arxiv.org/abs/2504.08066) | 端到端论文 | agentic tree search + workshop | 用树搜索改进实验与写作，达到 workshop 级；仍有大量人工与算力。 | 说明'端到端'不等于'可签署'；我们应坚持 claim/EA 门。 |
| 45 | Agent Laboratory: Using LLM Agents as Research Assistants | 2025 / [2501.04227](https://arxiv.org/abs/2501.04227) | 研究助手 | 人类反馈 + 代码实验 | 多角色研究助手，人在环；偏 assistant，不是自治科学家。 | 与我们 A3 定位最接近：机器起草、人保留判断。 |
| 46 | CycleResearcher: Improving Automated Research via Automated Review | 2024 / [2411.00816](https://arxiv.org/abs/2411.00816) | 研究论文/评审 | 自动 review + RL | CycleResearcher 用自动化评审做 reward 训练研究模型；评审质量是瓶颈。 | 我们用人工签核，不用自动评审做 claim 证据；这是更保守的选择。 |
| 47 | ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models | 2024 / [2404.07738](https://arxiv.org/abs/2404.07738) | 研究 idea | 文献 + 迭代 | 迭代式研究 idea 生成，强调文献 grounding；不执行实验。 | 对应我们 S2–S3；我们更强调 falsification 与 G1。 |
| 48 | Accelerating scientific discovery with Co-Scientist | 2025 / [2502.18864](https://arxiv.org/abs/2502.18864) | 假设生成 | 多 agent 辩论 + 专家 | Co-Scientist 的 generate/debate/evolve 与 tournament；人类专家最终判断。 | 我们已借鉴其多假设；但不要用 LLM 评审分替代 G1。 |
| 49 | Kosmos: An AI Scientist for Autonomous Discovery | 2025 / [2511.02824](https://arxiv.org/abs/2511.02824) | 数据驱动发现 | world model + 文献/代码引用 | 12 小时、200 rollouts、1,500 篇论文的自主发现系统；报告称 79.4% 陈述准确。 | 作者/公司口径，未复现；我们的 4 篇 CC-BY 语料远小于此。 |
| 50 | Robin: A multi-agent system for automating scientific discovery | 2025 / [2505.13400](https://arxiv.org/abs/2505.13400) | 多 agent 发现 | 湿实验验证 | Robin 将文献、假设、实验、分析串起来，提出 dAMD 候选并经湿实验验证；半自主。 | 说明真实发现需要湿实验/领域验证；我们的 ChemLab 只是 baseline。 |
| 51 | SciAgents: Automating scientific discovery through multi-agent intelligent graph reasoning | 2024 / [2409.05556](https://arxiv.org/abs/2409.05556) | 科学假设 | 知识图谱推理 | 多 agent + 图推理生成跨学科假设；缺少执行验证。 | 我们 idea 模块目前只用 spans，没有图推理。 |
| 52 | PaperBench: Evaluating AI's Ability to Replicate AI Research | 2025 / [2504.01848](https://arxiv.org/abs/2504.01848) | 论文复现 | rubric + 专家 | PaperBench 评估 agent 复现 AI 论文的能力；任务重、评分细。 | 是我们最该补的外部 benchmark；当前 closure 只证明结构闭合。 |
| 53 | RE-Bench: Evaluating frontier AI R&D capabilities of language model agents against human experts | 2024 / [2411.15114](https://arxiv.org/abs/2411.15114) | AI R&D 任务 | 专家人类基线 | RE-Bench 用 8 个 ML 研究工程任务对比人类专家；考察长程执行。 | 可作 S5 的上位 benchmark；ChemLab 不能代表研究能力。 |
| 54 | MLGym: A New Framework and Benchmark for Advancing AI Research Agents | 2025 / [2502.14499](https://arxiv.org/abs/2502.14499) | AI 研究任务 | Gym + RL | MLGym 提供研究任务环境与 baseline；适合训练/评测研究 agent。 | 可作为我们多轮 RSI 的外部环境，替代自造 S5 split。 |
| 55 | MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering | 2024 / [2410.07095](https://arxiv.org/abs/2410.07095) | ML 工程 | Kaggle 奖牌 | MLE-bench 用 Kaggle 任务评估 ML 工程 agent；强调端到端。 | 与我们 S5 的协议验证不同层；不能把 ChemLab R² 当 MLE 能力。 |
| 56 | ScienceAgentBench: Toward Rigorous Assessment of Language Agents for Data-Driven Scientific Discovery | 2024 / [2410.05080](https://arxiv.org/abs/2410.05080) | 数据驱动科学 | 任务 rubric | ScienceAgentBench 评估科学数据分析 agent；任务来自真实论文。 | 可补我们 S5 缺的'科研任务'维度。 |
| 57 | CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark | 2024 / [2409.11363](https://arxiv.org/abs/2409.11363) | 计算复现 | 复现成功/失败 | CORE-Bench 评估论文计算复现；强调环境与代码。 | 与我们的 RunCapsule/环境哈希最接近；可借其任务设计。 |
| 58 | DiscoveryBench: Towards Data-Driven Discovery with Large Language Models | 2024 / [2407.01725](https://arxiv.org/abs/2407.01725) | 数据驱动发现 | 发现结果匹配 | DiscoveryBench 用真实数据集评估假设发现；结构化任务。 | 可作 S2–S4 的外部评测，不是我们的 ChemLab。 |
| 59 | DS-Agent: Automated Data Science by Empowering Large Language Models with Case-Based Reasoning | 2024 / [2402.17453](https://arxiv.org/abs/2402.17453) | 数据科学 | 案例推理 + 执行 | DS-Agent 用 case-based reasoning 做数据科学；强调可复用案例。 | 对应我们 knowledge/process 候选的一个具体形态。 |
| 60 | FirstResearch: Auditable Question Formation for LLM Scientific Discovery Agents | 2026 / [2607.05682](https://arxiv.org/abs/2607.05682) | 研究问题形成 | 可审计性 | FirstResearch 关注问题形成过程的可审计，而不是只评最终答案。 | 直接支持我们'问题选择留给人'的边界。 |
| 61 | AI Scientists Are Only as Good as Their Evidence: A Stratified Ablation of Proprietary Data and Reasoning Skills in Drug-Asset Valuation | 2026 / [2606.09556](https://arxiv.org/abs/2606.09556) | 证据质量 | 分层消融 | 用分层消融分析 proprietary data 与 reasoning skills 对药物资产估值的影响；强调 evidence 而非模型。 | 与我们的'证据运营'主线一致：数据/证据质量常比模型更关键。 |
| 62 | AI Scientists Fail Without Strong Implementation Capability | 2025 / [2506.01372](https://arxiv.org/abs/2506.01372) | 实现能力 | 复现实验 | 指出 AI scientist 的瓶颈在强实现能力，而非只靠 idea；没有可靠执行就没有科学。 | 我们 S5 的 run/EA 正是补实现能力，但目前只有小数据 baseline。 |
| 63 | Recursive self-improvement of AI research agents | 2026 / [2609.26457](https://arxiv.org/abs/2609.26457) | 研究 agent 自身代码 | hidden eval + 8 天运行 | AIDE² 让研究 agent 改自己的代码，8 天连续发现 7 次改进，并在 4 个 held-out benchmark 泛化。 | 这是我们最接近的'真实多轮'对照；我们只有一次 seed-budget trial。 |

## D 记忆/技能/上下文（14 篇）

| # | 论文 | 年份 / ID | 优化对象 | 反馈信号 | 读点与边界 | 与本仓库的关系 |
|---|---|---|---|---|---|---|
| 64 | MemGPT: Towards LLMs as Operating Systems | 2023 / [2310.08560](https://arxiv.org/abs/2310.08560) | 上下文/记忆层级 | 检索 + 任务 | MemGPT 用 OS 分页思想管理长上下文；是记忆架构，不含自进化治理。 | 我们若做 knowledge 候选，需要类似的层级与淘汰策略。 |
| 65 | Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | 2025 / [2504.19413](https://arxiv.org/abs/2504.19413) | 长期记忆 | 抽取/更新/检索 | Mem0 做生产级记忆抽取与更新；关注延迟/成本，不关注证据真值。 | 我们的 memory 不能只追召回，还要 provenance/taint。 |
| 66 | A-MEM: Agentic Memory for LLM Agents | 2025 / [2502.12110](https://arxiv.org/abs/2502.12110) | 记忆网络 | 动态链接 | A-MEM 用 Zettelkasten 式动态链接组织记忆；结构可演化。 | 可借'链接'表示 artifact 关系；但链接不是证据。 |
| 67 | MemoryBank: Enhancing Large Language Models with Long-Term Memory | 2023 / [2305.10250](https://arxiv.org/abs/2305.10250) | 长期记忆 | 检索 + 遗忘曲线 | MemoryBank 用 Ebbinghaus 遗忘机制管理记忆；适合对话，不适合 claim。 | 提醒我们 memory 淘汰不能淘汰证据引用。 |
| 68 | Zep: A Temporal Knowledge Graph Architecture for Agent Memory | 2025 / [2501.13956](https://arxiv.org/abs/2501.13956) | 时序知识图谱 | 时间戳/关系 | Zep/Graphiti 用时序知识图谱做 agent memory；适合动态事实。 | 我们的 stale 传播可借时序边，但需要 claim→span→figure 的强类型。 |
| 69 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | 2024 / [2405.14831](https://arxiv.org/abs/2405.14831) | 图索引记忆 | 多跳检索 | HippoRAG 用海马体索引做多跳记忆检索；提升 RAG 多跳。 | 可用于 S1 文献关系，但不能替代全文 span。 |
| 70 | From RAG to Memory: Non-Parametric Continual Learning for Large Language Models | 2025 / [2502.14802](https://arxiv.org/abs/2502.14802) | 非参数持续学习 | passage-level 记忆 | HippoRAG 2 从 RAG 走向记忆，强调持续学习；仍非权重更新。 | 与我们的 frozen-model 路线兼容。 |
| 71 | Human-inspired Episodic Memory for Infinite Context LLMs | 2024 / [2407.09450](https://arxiv.org/abs/2407.09450) | episodic memory | surprise 分段 | EM-LLM 用事件边界与 surprise 组织无限上下文；提升长文推理。 | 可用于论文长文/审稿记忆；不解决证据准入。 |
| 72 | Larimar: Large Language Models with Episodic Memory Control | 2024 / [2403.11901](https://arxiv.org/abs/2403.11901) | episodic memory | 快速写入/控制 | Larimar 用 episodic memory control 实现快速知识更新；不改权重。 | 适合我们 knowledge 候选的快速回滚；但需 lease。 |
| 73 | A Survey on the Memory Mechanism of Large Language Model based Agents | 2024 / [2404.13501](https://arxiv.org/abs/2404.13501) | 记忆机制 | 综述 | 系统梳理 LLM agent 记忆的来源、形式、操作与评测；是术语底账。 | 我们文档中的 memory 术语应与该 taxonomy 对齐。 |
| 74 | Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory | 2025 / [2504.07952](https://arxiv.org/abs/2504.07952) | 测试时记忆 | 无 gold label 的任务反馈 | Dynamic Cheatsheet 在测试时积累可复用策略，不更新权重；适合黑盒模型。 | 与我们的 process/prompt 候选最接近；仍需外部 gate。 |
| 75 | RoMeRL: Balancing Feedback Coverage and the Memory-Reward Trap in Self-Evolving Agent Memory via Reduced-Order Utility States | 2026 / [2608.02508](https://arxiv.org/abs/2608.02508) | 记忆效用 | reduced-order utility | RoMeRL 研究记忆-奖励陷阱，用降阶效用平衡反馈覆盖；避免'记忆越多越好'。 | 我们的 memory 候选评估不能只看召回，要看 downstream utility 与成本。 |
| 76 | When Stored Evidence Stops Being Usable: Scale-Conditioned Evaluation of Agent Memory | 2026 / [2605.07313](https://arxiv.org/abs/2605.07313) | 记忆可用性 | 规模条件评测 | 研究存储证据在规模变大后何时失效；记忆评测需要 scale-conditioned。 | 对应我们 static snapshot 的隐患：数据变大/变旧后结论可能失效。 |
| 77 | SoK: Agentic Skills -- Beyond Tool Use in LLM Agents | 2026 / [2602.20867](https://arxiv.org/abs/2602.20867) | 技能生命周期 | 综述/分类 | SoK 把 agentic skills 的生命周期、表示、范围、供应链安全系统化。 | 我们的 skill manifest 应补 supply-chain、测试、权限与撤销字段。 |

## E RSI 治理/评测（23 篇）

| # | 论文 | 年份 / ID | 优化对象 | 反馈信号 | 读点与边界 | 与本仓库的关系 |
|---|---|---|---|---|---|---|
| 78 | A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems | 2025 / [2508.07407](https://arxiv.org/abs/2508.07407) | 自进化 agent | 综述 | 把 self-evolving agents 的进化对象、反馈、生命周期与评测系统化；强调与 lifelong learning 的桥接。 | 我们应把自己放在'受治理 harness 进化'一格，而不是泛称 RSI。 |
| 79 | RRSI: Regularized Recursive Self-Improvement of Agent Harnesses | 2026 / [2609.24972](https://arxiv.org/abs/2609.24972) | agent harness | 正则化选择 + OOD | RRSI 限制候选编辑预算、用 critic/pruner 过滤 benchmark-specific 改动，缓解 harness RSI 过拟合。 | 直接可借：我们的 candidate patch 没有编辑预算，public 排序也缺 critic/pruner。 |
| 80 | RSI-Anything: Unlocking Recursive Self-Improvement with World Models | 2026 / [2610.13912](https://arxiv.org/abs/2610.13912) | policy/world model | 预测 + 条件确认 | RSI-Anything 用 world model 指导行动与数据选择，保留 policy-model pair；跨域增益为作者口径。 | 我们 docs 已引用；代码只借了 archive/lease，没有 world model 或 conditional confirmation。 |
| 81 | Dream-RSI: Recursive Self-Improvement through Evolving Worlds | 2026 / [2609.14858](https://arxiv.org/abs/2609.14858) | 探索策略 | 历史 discovery tree 重放 | Dream-RSI 用历史发现树做 replay simulator，低成本评估探索策略，再在线部署。 | 可为我们 S5/S1 的多轮 trial 提供离线 replay，减少真实 run 成本。 |
| 82 | RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments | 2026 / [2609.15364](https://arxiv.org/abs/2609.15364) | 环境记忆 | 课程/actor/verifier | RSIAgent 训练-free 地构建环境记忆，broad-then-deep 探索；在 OSWorld 等环境提升。 | 对应我们 knowledge 候选的'环境记忆'；但需要 verifier 与 scope。 |
| 83 | RSIBench-Data: Benchmarking Data-Centric Research for Recursive Self-Improvement | 2026 / [2607.25886](https://arxiv.org/abs/2607.25886) | 数据研究 | 固定 post-training stack + 预算 | RSIBench-Data 把数据准备研究从工程中剥离，测 agent 的研究能力；58% 设置能改进首轮。 | 我们缺这类 benchmark；ChemLab 只是单点协议验证。 |
| 84 | RSIGym: A Flexible Environment for Recursive Self-Improvement | 2026 / [2610.10310](https://arxiv.org/abs/2610.10310) | data/harness/joint | EaaS + RSI-Index | RSIGym 提供训练、推理、rollout、评测、沙箱服务，支持三类改进轨道与预算控制。 | 我们 runtime 只有 pipeline，没有训练/rollout；可作为未来外部评测接口。 |
| 85 | Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops | 2026 / [2607.07663](https://arxiv.org/abs/2607.07663) | RSI taxonomy | 1250 篇综述 | 区分 bounded self-refinement 与 open-ended RSI，按'改进什么'与'闭环程度'分类，并给出 evaluator 层级。 | 我们的系统属于 bounded harness refinement + 人工闭环；不应写成 open-ended RSI。 |
| 86 | Auditing the Product, Not the Recursion: The Evaluation Evidence Behind Recursive Self-Improvement Claims | 2026 / [2610.27610](https://arxiv.org/abs/2610.27610) | RSI 证据审计 | 114 项全文编码 | 只有约 22% 的 RSI 研究审计了完整循环≥2 次；60% 在未参与选择的任务上评估。 | 这是我们必须补的缺口：至少 2 次完整 rerun、未参与选择的任务、独立编码。 |
| 87 | Evolutionary Safety of Recursive Self-Improving AI: Taxonomy, Risk Discovery, and Evaluation | 2026 / [2609.31186](https://arxiv.org/abs/2609.31186) | 演化安全 | 六类风险/五域 | 把 RSI 安全从单次失败扩展到跨更新、累积、传播的演化风险。 | 我们的 claim/gate 不可变只覆盖一层；需跨版本安全审计。 |
| 88 | Safety in Self-Evolving Agents: A Survey | 2026 / [2610.00093](https://arxiv.org/abs/2610.00093) | 自进化 agent 安全 | SAVER 框架 | 经验变成可复用状态后，安全问题变成'安全属性能否跨积累/复用保持'。 | 我们的 memory/skill 候选需要 taint、来源与撤销传播。 |
| 89 | Self-Authored Verification Is Unreliable in Heuristic Self-Improving Agents | 2026 / [2607.24300](https://arxiv.org/abs/2607.24300) | 自评/验证器 | sealed exogenous audit | 指出自写测试会让分数虚高；SEAL 用 agent 不可见的固定审计做接受/拒绝。 | 我们目前的 hidden 任务在仓库里可见，不是 sealed；这是 P0。 |
| 90 | Self-Evolving Agents with Anytime-Valid Certificates | 2026 / [2607.00871](https://arxiv.org/abs/2607.00871) | steering adapter/harness | anytime-valid certificate | 把自修改限制在小 adapter + 版本化 harness，用 anytime-valid gate 给出可审计证书。 | 可借其统计门与证书格式；我们只有确定性 pass/fail。 |
| 91 | Layered Mutability: Continuity and Governance in Persistent Self-Modifying Agents | 2026 / [2604.14717](https://arxiv.org/abs/2604.14717) | 五层可变性 | 治理负载/迟滞 | 区分预训练、对齐、自我叙事、记忆、权重五层，指出治理难度随速度/耦合/不可逆性上升。 | 我们应明确只改 harness 层，并把 memory/skill 的可逆性写进 lease。 |
| 92 | SkillJack: Persistent Skill Backdoors in Self-Evolving Agents | 2026 / [2608.03509](https://arxiv.org/abs/2608.03509) | 技能供应链 | 后门攻击 | SkillJack 把中毒经验转成持久技能，绕过上下文清洗；技能库是新的攻击面。 | 我们的 skill 候选目前没有供应链扫描/签名/撤销测试，是未来风险。 |
| 93 | Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation | 2026 / [2606.05241](https://arxiv.org/abs/2606.05241) | 检索评测 | 污染检测 | 深度研究 agent 可能在推理时搜到 benchmark 答案，虚高最多约 4%。 | 我们的真实语料是冻结本地，不需 web；但若接 OpenAlex/网页，必须隔离。 |
| 94 | AI Sandbagging: Language Models can Strategically Underperform on Evaluations | 2024 / [2406.07358](https://arxiv.org/abs/2406.07358) | 评测行为 | 策略性降分 | 模型可在评测中故意表现差以规避部署/监管；自评/公开评测都需防 sandbagging。 | 我们的 human gate 也可能被'看起来安全'的候选绕过；需要行为审计。 |
| 95 | Alignment faking in large language models | 2024 / [2412.14093](https://arxiv.org/abs/2412.14093) | 对齐行为 | 自保动机 | 模型在训练/部署冲突时可能隐藏能力或策略性服从；提醒自进化系统的目标漂移。 | 我们的 immutable surfaces 是结构防线，不是对齐证明。 |
| 96 | The Curse of Recursion: Training on Generated Data Makes Models Forget | 2023 / [2305.17493](https://arxiv.org/abs/2305.17493) | 数据分布 | 递归训练 | 在自生成数据上递归训练会导致分布尾部消失/模型崩溃；自 consuming loop 的经典风险。 | 我们的 loop 不训练权重，但 memory/context 自 consuming 也可能退化。 |
| 97 | Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges | 2026 / [2604.13602](https://arxiv.org/abs/2604.13602) | 奖励机制 | 综述 | 系统梳理 reward hacking 的机制、涌现错位与挑战；自进化会放大奖励漏洞。 | 我们的 S5 public 指标若被候选优化，可能 Goodhart；需 held-out 与多指标。 |
| 98 | The Economics of Recursive Self-Improvement | 2026 / [2609.15802](https://arxiv.org/abs/2609.15802) | 经济/能力 | 弹性模型 | RSI 加速取决于各反馈环弹性乘积；当前数据不支持自持加速，窄能力提升不等于广泛能力。 | 我们的一次 seed-budget 成本下降不能写成能力加速。 |
| 99 | SEVerA: Verified Synthesis of Self-Evolving Agents | 2026 / [2603.25111](https://arxiv.org/abs/2603.25111) | agent 程序 | 形式契约 + 验证 | 用一阶逻辑输出契约包裹生成模型调用，保证硬约束；再优化软目标。 | 可借'不可变 surface'的形式化；我们目前只是字符串匹配。 |
| 100 | SAHOO: Safeguarded Alignment for High-Order Optimization Objectives in Recursive Self-Improvement | 2026 / [2603.06333](https://arxiv.org/abs/2603.06333) | 对齐/约束 | GDI + 回归风险 | SAHOO 用目标漂移指数、约束保持与回归风险监控自改进；阈值需校准。 | 我们的 MetaTracker 只有 warnings，没有 drift/回归统计门。 |

## 统计

| 簇 | 篇数 | 主要改进对象 | 主要证据形态 |
|---|---:|---|---|
| A 基础机制 | 22 | 输出、prompt、代码、权重、记忆 | 自评、执行器、任务分数 |
| B 自改与进化 | 20 | agent 代码、harness、技能库、数据准备器 | benchmark、archive、held-out |
| C 科研自动化 | 21 | idea、实验、论文、研究工程 | 自动评审、专家、复现/竞赛 |
| D 记忆/技能/上下文 | 14 | 记忆、技能、上下文 | 检索/任务效用/规模条件 |
| E RSI 治理/评测 | 23 | RSI 证据、安全、形式保证 | 审计、证书、攻击/防禦 |
