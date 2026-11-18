# 差异化反思：从“生成科研”到“证据变更后的维护与重闭合”

> 日期：2026-10-25  
> 依据：本地 14/36/39/42 的反思、Cortex 对照审计、本轮实测的 closure/lineage/waitpoint/maintenance 代码与 144 个测试。  
> 目的：回答一个答辩和产品都绕不开的问题——**市面上已经有很多科研 Agent，我们到底哪里不同，凭什么值得存在？**

## 0. 一句话结论

**别人优化“更快生成一篇论文”，我们优化“证据变了以后，哪一句还成立、哪一步必须重跑、哪一个导出必须被拦住，以及谁重新签名”。**

不是“再来一个 AI Scientist”，也不是“多 Agent 工作台”。我们更准确的定位是：

> **科研证据的变更维护层（evidence maintenance layer）**：围绕已存在的 claim、EA、图、稿件槽位、closure 与 signature，做内容寻址、失效传播、三类处置、重新闭合与可签署导出。

这个定位比“端到端科研”窄，但更硬、更可测，也更贴近 2026 年科研 Agent 真正被低估的失败面。

## 1. 市面上的工作各自在优化什么

只按公开材料能确认的机制比较，不比较未复现的效果数字；“没有展示”不等于“做不到”。

| 类别 | 代表 | 优化对象 | 到生成/审计为止 | 没有强制的部分 |
| --- | --- | --- | --- | --- |
| 端到端科研生成 | AI Scientist、Co-Scientist、DeepScientist | 从问题到想法、实验、论文/评审 | 有生成、有自动评审或工作区 | 生成后的证据变更、旧结论失效、导出重闭合 |
| 生成时证据绑定 | ScientistOne/CoE | 写作时的 claim→引用/数值/方法/代码对齐 | 有较强的生成时验证与审计 | 已有稿件的跨版本维护、修复队列、重签 |
| 事后完整性审计 | ARIS / Anti-Autoresearch | 对第三方论文做 evidence ledger、引用/基线/实验审计 | 有可定位报告、可阻断投稿 | 修复执行、重新闭合、版本化签署 |
| 编辑传播测量 | EditPropBench | 局部事实编辑是否触发非局部修订 | 有任务与测量 | 运行时处置、实验重跑、导出门 |
| 长时 Agent 工作台 | Cortex | 跨 session 工作、team、memory、waitpoint、开发/GPU 工具 | 有强执行与协作底座 | claim/EA 的权限化、闭合后失效传播 |
| 文献/写作工具 | Elicit、Consensus、PaperQA、中文证据链产品 | 检索、引用、写作体验 | 有检索/写作/引用核验 | 独立重跑、run-bound claim、导入/导出硬门 |

这张表说明一件重要的事：**“把 claim 绑到证据”已经是入场券，不再是主卖点。** 我们不能把“证据链”三个字单独当创新；它已经被 CoE、ARIS 和中文产品大量使用。

## 2. 我们现在真正拥有的差异化

### 2.1 不是“更多 Agent”，而是“对象 + 不变量 + 变更语义”

当前仓库的实际对象链是：

```text
SourceHit → Span → CoverageReceipt/Gap
                 ↘
RunCapsule → EA → Claim → Protocol/Bibliography/Figure
                         → Paper slots → Closure → Signature → immutable bundle
```

已落地的、可被代码核验的部分：

- **run-bound claim**：claim 通过 EA 绑定 run；没有 EA 不能进入 claim；
- **closure 事实校验**：closure 现在不仅看 demo 内嵌字段，还校验 protocol/bibliography/result-figure 的伴随文件、id/status/hash；bibliography 的 entries 会重新计算哈希；
- **不可变证据 bundle**：`closure publish` 把已签 manifest 列出的证据复制到 staging，逐文件重建 sha256，fsync 后原子 rename；目标已存在即失败；`verify-bundle` 可重新发现篡改；
- **内容寻址的 stale 传播**：lineage 把 dataset/code/run/EA/claim/figure/slots/closure/signature 建成依赖图；变更沿边传播为 stale；
- **三类维护处置**：本轮新增，`impact` 不只报红，还把 stale 节点映射成 `rerun / rewrite / recheck`，并给出 `action_counts` 与有序 `next_steps`；
- **导出否决**：`export_allowed=false`，旧 signature 失效；`--fail-on-stale` 返回非零，可直接进 CI/签署前门；
- **本地 waitpoint**：外部训练/评测可用 `create → signal → inbox/consume` 回传，不轮询、不联网、不自动签名；为后续长任务接入留下真实原语。

真实 demo 的当前结果：

```text
数据/代码变更 → 2 rerun / 6 rewrite / 7 recheck
               → closure + signature stale
               → EXPORT BLOCKED
               → 按 next_steps 重跑/重绑/重闭合/重签
```

这比“又写出一篇论文”更适合被审查：**它展示的是系统如何拒绝继续导出，而不是如何假装完成。**

### 2.2 与最接近工作的差异

| 对手/邻近工作 | 它已经做了什么 | 我们的差异点 | 我们不能声称什么 |
| --- | --- | --- | --- |
| CoE / ScientistOne | 生成时把 claim 绑到引用/数值/方法/代码 | 我们把已闭合产物的**变更后失效**与处置做成运行时对象 | 不能声称“写作时证据绑定”是首创 |
| ARIS / Anti-Autoresearch | 对第三方论文/仓库做事后审计、可定位报告 | 我们不只出报告，还给出 `rerun/rewrite/recheck` 和 `EXPORT BLOCKED`，并指向重新签署 | 不能声称“事后审计”是空白 |
| EditPropBench | 测量局部事实编辑的非局部传播 | 我们不只测量传播，还把传播映射到科研工件的处置与导出门 | 不能声称“失效传播”概念无人做过 |
| Cortex | 长时运行、team、waitpoint、文件式 memory | 我们把这些能力用于**结论权限化**：claim/EA/closure/signature 在模型 loop 外，审批不能被 Agent 自写 | 不能声称工作区/团队/记忆能力超过 Cortex |
| AI Scientist / Co-Scientist | 端到端生成与评审 | 我们主动放弃“自动生成全文”的正面竞争，做其证据维护层 | 不能声称端到端科研能力领先 |

一句话：**CoE/ARIS 证明“证据绑定/审计”会商品化；真正稀缺的是“证据变化后仍能负责地交付”的组合。**

## 3. 我们的差异化不应该建在什么上

以下内容可以作为体验/基础，但不能作为核心 novelty：

- 多 Agent 仪表盘、更多阶段、更多角色：容易同质化，且我们的代码主要是确定性模块；
- Skill 目录/模型选择/聊天 UI：Claude Code、Cortex 和通用 Agent 已很强；
- “写作时绑定证据”：已有 CoE/ARIS/中文产品；
- “RAG 记忆”：Cortex 的 Dense Context 与普通 RAG 都能做；
- RSI/自进化能力增益：E7/E8 未跑，hidden 还不是独立数据；
- 自动生成论文：paper 模块只有槽位，没有正文生成。

这些不是删除，而是**降级为支撑层**，不要抢标题。

## 4. 还缺什么，才能把差异化说完整

当前已有“变更 → stale → 处置 → recheck-only reclose → 人签 → bundle”。还没有完成：

1. **ChangeSet 对象**：现在的变更来自哈希对比；需要显式记录“谁在何时因为什么改了数据/代码/协议/引用”，并绑定 actor/reason。
2. **完整重闭合执行器**：`maintenance.reclose` 只覆盖 recheck-only；`rerun/rewrite` 仍需新的 run → EA → claim → slots → closure → sign 执行链。
3. **S1→Claim 显式边**：文献 span 还没有进入 claim 依赖图；否则只能维护结果臂，不能维护文献句。
4. **句子级映射**：目前是 5 个大槽位；需要 paper 句子/段落 → claim/span 的边，才能只重写受影响段落。
5. **签名身份**：现在的 signature 是 JSON 记录；需要 signer 身份/公钥/签名验证，否则“人签”仍是文件写权限。
6. **语义支持/abstention**：closure 仍是结构检查；不能判断 claim 文本是否语义上被 span 支持。需要标注集、P/R、abstention，不把 LLM judge 当真理。
7. **真实数据臂**：S1 只有冻结 CC-BY 语料；OpenAlex 摘要不生成 span。需要全文/页码/字符偏移，才能让 maintenance 在真实主题上跑。
8. **runtime 接入**：waitpoint 只有原语与 CLI；还没有把 wake 接回持久 job 与 agent loop。

这些缺口应该按“信任边界 → 真实数据 → 维护执行 → 语义支持”的顺序补，而不是再加 Agent。

## 5. 产品楔子：Evidence Change Maintenance

### 5.1 用户故事

> 我把一份已经签过的研究包交给系统，改了一个数据集/代码版本/引用。  
> 系统告诉我：哪些 claim 失效、哪张图需要重生成、哪些 slots 需要重写、哪些只需复核；  
> 我按顺序重跑、重绑、重闭合，最后重新签名；旧版本保留，导出保持 blocked 直到完成。

这不是“AI 自动做科研”，而是一个**可交付的证据维护工作台**。用户不需要相信模型会科研，只需要相信系统会在证据失效时拦住他。

### 5.2 三分钟演示

1. 打开「证据沿袭」：17 节点、11 checks、1 claim、signature，`EXPORT OK`。
2. 模拟数据集变更：`2 RERUN / 6 REWRITE / 7 RECHECK`；`EXPORT BLOCKED`。
3. 展开一个 claim：upstream EA/run、downstream slots/closure/signature 全部可见。
4. 展示处置顺序：重跑 S5 → 重封 EA/claim → 重绑图/槽位 → 重跑 closure → 人签 → 才允许导出。
5. 展示不可变 bundle/verify-bundle：签名后的字节可复核；不是一张报告截图。
6. 说明 waitpoint：真实外部训练结束后通过 CLI 回传，而不是轮询/占着 turn。

处置卡截图：`docs/frontend-audit/282-dispositions-1440.png`、`283-dispositions-390.png`。

### 5.3 可以对外说的句子

> 我们不与通用科研 Agent 比“生成的论文更多”，而是做它们的**证据变更维护层**：当数据、代码、协议或引用变化时，系统把受影响的 claim、图、槽位、closure 与 signature 传播为 stale，给出 rerun/rewrite/recheck 处置，并在重新闭合与人工签署前拒绝导出。

这句话不依赖“首个/唯一/零幻觉”等不可证主张。

## 6. 8 周最小验证

| 周 | 交付 | 验收指标 |
| --- | --- | --- |
| 1–2 | ChangeSet schema + actor/reason；impact 接收显式 ChangeSet | 10 个手写变更案例，处置分类正确率 ≥90% |
| 3–4 | Reclosure runner：从 ChangeSet 走到 new EA/claim/slots/closure | 至少 3 个案例端到端重闭合；旧导出保持 blocked |
| 5–6 | 句子级 mapping（先做结果/引用两类槽位） | 受影响句子召回 ≥80%，误报 ≤20% |
| 7 | signature 身份 + verify；bundle 锚点 | 伪造/篡改测试全部阻断 |
| 8 | 真实数据臂 + 对照实验 | 与手工 diff/全量重跑对比，记录时间、错误、导出状态 |

**Kill criteria**：如果 10 个真实变更案例中，处置分类不能稳定优于“全量重跑”或“人工 diff”，或者用户仍无法信任 export gate，那么这一定位需要重估；不要用 UI 动画掩盖。

## 7. 结论

我们最有差异化的地方，不是“能生成科研内容”，而是：

> **当证据变化时，系统能明确指出哪些结论不再成立，并拒绝让旧签名继续导出；修复后必须重新闭合、重新签署。**

这条路比“再造一个 AI Scientist”窄，但更难被商品化叙事替代，也更容易用代码、测试和一次真实变更演示来证明。我们要把有限的工程时间押在这里，而不是继续加 Agent、阶段或仪表盘。

延伸阅读：[DEEP-REFLECTION.md](DEEP-REFLECTION.md)（证据/权限/变更/运行时四个底层模型，以及 12 周优先级与 kill criteria）。

理论边界：[THEORY-REFLECTION.md](THEORY-REFLECTION.md)。

API 状态：[API-INTEGRATION.md](API-INTEGRATION.md)。
