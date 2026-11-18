# 理论反思：我们能不能真的达到“好效果”？

> 日期：2026-10-25  
> 对象：evidence runtime、lineage dispositions、maintenance plan/reclose、closure bundle、waitpoint、前端 BRIEF。  
> 问题：这些底层逻辑在理论上成立吗？在什么条件下能产生实际效果？哪些结论现在还不能说？

## 0. 先给判断

**当前设计可以达到“局部完整性”，还达不到“全局语义正确性”。**

把它分成三层更准确：

| 层 | 目标 | 理论状态 | 当前实现 |
| --- | --- | --- | --- |
| 完整性 | 声明依赖图上的变更不漏、旧导出被拦住 | 在声明图完整、门禁唯一时成立 | 部分成立 |
| 维护性 | 减少重新核查/重跑/重写的人工成本 | 有条件成立 | 有原型，未实测 |
| 语义正确性 | claim 真的被证据支持、结论真的正确 | 目前不成立 | 只有结构检查 |

所以“能不能达到很好的效果”不是一个 yes/no，而是一个条件命题：

> **如果依赖边覆盖足够高、导出只有一个强制执行点、处置精度足够高、并且有真实维护基准，那么它可以显著减少“旧证据继续被交付”的风险；否则它会退化为一个会制造告警疲劳的 stale 仪表盘。**

---

## 0.1 理论依据分级：不是所有反思都一样硬

先把“有依据”拆开，否则很容易把设计直觉说成理论保证。

| 主张 | 依据类型 | 当前确定性 | 还缺什么 |
| --- | --- | --- | --- |
| 声明依赖图 D 上的下游闭包不会漏掉 D 内受影响节点 | 集合论/构建系统理论 | **条件定理**：给定 D 完整 | 证明 D 覆盖真实 S；当前不成立 |
| 选择性重跑/重建可以避免全量工作 | 增量构建的 early cutoff/minimality 理论 | **条件成立** | 依赖边、缓存、隔离与边界条件 |
| “没有有效签名不能导出”可以成为安全属性 | reference monitor / complete mediation / least privilege | **条件定理**：需要唯一门禁、不可篡改、可验证 | 当前没有 reference monitor |
| 内容哈希能发现字节变化 | 密码学哈希的完整性假设 | **工程上成立** | 抗碰撞、可获取原始字节、外部锚点 |
| claim 的来源可被追溯 | 数据 provenance 理论（why/where/how） | **表示层成立** | 语义支持、边覆盖、来源版本 |
| 维护计划能减少人工时间 | 成本/人因模型 | **假设** | 真实变更基准与对照实验 |
| rerun/rewrite/recheck 分类正确 | 启发式策略 | **弱假设** | 变更类型、scope、边类型与标注集 |
| 人签能提高责任性 | 人因/自动化偏差理论 | **条件成立** | 身份、证据摘要、摩擦、自动化偏差缓解 |
| 证据维护层是市场空位 | 市场调研 | **策略假设** | 用户访谈、竞品持续跟踪、真实采用 |
| closure 通过等于结论正确 | 无 | **不成立** | 语义支持与 abstention 评估 |

这张表的意思很直接：**我们整体反思的“骨架”有理论依据，但“效果”和“差异化”只有条件和假设，不是已经证明的定理。**

## 1. 形式化：stale 传播到底保证了什么

设：

- `A` 是 artifact 集合；
- `C` 是发生变化的 artifact；
- `D` 是我们**声明**的依赖边图；
- `S` 是**真实语义**依赖边图。

`stale_D(C)` 是在 `D` 上对 `C` 做下游闭包。理论上有：

```text
如果 S ⊆ D（所有真实依赖都被声明），则 affected_S(C) ⊆ stale_D(C)
  → 不会漏掉受影响节点（sound，但可能过度）
如果 D ⊆ S（每条声明边都真实存在），则 stale_D(C) ⊆ affected_S(C)
  → 不会误报（precise，但可能漏掉）
只有 D = S，才同时 sound 且 precise。
```

当前系统显然不是 `D = S`：

- **缺边**：S1 span→claim、claim→稿件句子、环境/依赖版本→run、引用撤稿→文献句、数据语义→指标；这些没有进入图；
- **过粗**：paper、closure 作为整节点依赖，某个 slot 变化会让整篇 paper stale；一个 bibliography 变化可能让整段 paper 重写，即使结果 claim 不受影响；
- **来源不对**：dataset/code 节点哈希目前来自 capsule 字段，不是从当前文件重算；capsule 字段不变而文件变了，图可能仍 clean。

因此当前能说的是：

> **在已声明节点和已实现哈希上，变更会被传播；不能声称覆盖真实科研语义依赖。**

这是理论上最重要的边界。

### 1.1 处置映射不是定理，是策略

`rerun / rewrite / recheck` 目前主要由节点 kind 决定：

```text
run/evidence → rerun
figure/slot/paper → rewrite
其余 → recheck
```

这只是一个 **policy prior**，不是从语义推导出来的。例如：

- 改了一个引用格式，bibliography 变了，但 claim 的数值结果不受影响；全部 recheck 可能过度；
- 改了数据生成脚本的一个无关注释，code hash 变了，但 run 语义没变；直接 rerun 可能浪费；
- 改了 claim 的措辞，scope 没变，可能只需 recheck；
- 改了 claim 的 scope，即使 statement 不变，也可能必须重新评估全部支撑。

理论上正确的处置需要：

```text
edge type: supports | derives | binds | invalidates
scope: 数据/代码/语义/格式/版本
change type: value | scope | metadata | source
```

没有这些，处置只能是启发式，不能保证“处置正确”。

### 1.2 自动 reclose 的理论风险

`maintenance.reclose` 目前只对 `recheck-only` 自动重跑 closure。这个策略的假设是：

> 没有 rerun/rewrite，就说明没有新的证据需要产生，closure 可以安全重跑。

这个假设只有在 `D` 覆盖所有语义依赖且 closure 能判断语义支持时才成立。当前两者都不完全成立，所以自动 reclose 仍可能产生**虚假安心**：

```text
漏边 → 影响未传播 → plan 认为只需 recheck
     → closure 结构通过
     → ready_for_resign
     → 人签
     → 一个语义上已失效的结论被重新签署
```

所以自动 reclose 的正确边界应该更窄：

- 只对 **source/metadata-only** 且不触及 claim 语义的变化自动；
- 任何 claim/scope/数据/代码语义变化默认进入人工复核；
- 在 `D` 的覆盖率被测量之前，不应把“自动 reclose”当成安全保证，只能当效率优化。

---

## 2. 权限：reference monitor 是否成立？

如果把“没有有效签名就不能导出”当成安全属性，需要满足经典 reference monitor 条件：

1. **complete mediation**：所有导出路径都经过同一个门；
2. **tamper-proof**：执行 Agent 不能改门/签名/审计；
3. **verifiable**：门能验证签名、身份、授权和输入哈希。

当前系统：

- 有 CLI `closure publish`，但本地文件仍可被手工写 manifest/signature；
- closure 仍从 demo 读取 capsule status；
- signature 是普通 JSON，没有 signer 公钥/验签；
- 前端静态模式可以“模拟签署”，没有服务端强制；
- runtime 没有 auth，本地文件写权限就是最高权限。

因此目前**不满足 reference monitor**，不能把“旧导出一定被拦住”当成系统保证。可验证的只是：

> 在遵守 CLI/工具链、且外部存在可信锚点的前提下，bundle 的字节可被重算和比对。

### 2.1 哈希不等于真实性

内容哈希只能回答“这些字节是否相同”，不能回答：

- 谁创建了它；
- 它是否来自真实实验；
- 它是否被正确解释；
- 签名者是否理解自己签的内容。

`bundle-manifest` 本身也可以被重写；`publish` 返回的 `manifest_sha256` 若没有写入外部可信记录/lineage/签名，攻击者可以同时改 bundle 与 manifest。当前实现已在文档中承认这一边界。

### 2.2 人签不等于理解

即使有 Ed25519，签名也只证明“某个 key 对某个 payload 签了名”。它不能证明：

- signer 看了证据；
- signer 理解 scope/limitations；
- signer 没有利益冲突；
- signer 没有被 UI 的“默认批准”诱导。

所以人类因素必须进入理论模型：签名是一个**社会技术协议**，不是密码学函数单独能解决的。

---

## 3. 维护效果：一个条件收益模型

设：

- `P(change)`：项目在维护周期内发生证据变化的概率；
- `C_full`：全量重跑/人工复查成本；
- `C_maint`：选择性维护成本；
- `C_fp`：误报导致的额外复核成本；
- `C_gate`：门禁摩擦/等待/沟通成本；
- `R`：受影响对象召回率；`P_prec`：处置精度。

粗略地：

```text
期望收益 ≈ P(change) × [R × (C_full - C_maint) - (1 - P_prec) × C_fp - C_gate]
```

这个式子说明：

- 如果 `R` 低，收益可能为负：该修的没修，风险转成事故；
- 如果 `P_prec` 低，用户会逐渐绕过 gate；
- 如果 `C_gate` 高，即使技术上正确，产品也不可用；
- 如果变化很少（`P(change)` 低），维护层的价值不足以抵消接入成本。

当前没有 `R`、`P_prec`、`C_maint` 的测量，因此**不能从理论直接推出“效果会好”**。只能提出可检验假设。

---

## 4. 长任务与 waitpoint 的理论边界

waitpoint 的 `create → signal → consume` 只保证：

- 在本地文件系统上，secret 正确时可以写入一个 signal；
- signal 可被消费一次（通过 delivered 标记）；
- TTL/成员/幂等有明确规则。

它**不保证**：

- 外部进程真的执行了它声称的任务；
- 信号没有被泄露 secret 的第三方伪造；
- 多进程下 exactly-once（目前是本地锁 + at-most-once delivery 语义，崩溃窗口仍需处理）；
- 唤醒后 Agent 会正确恢复（目前没有 loop 接入）。

因此 waitpoint 的理论价值是**降低轮询成本与延迟**，不是“证明外部结果正确”。外部 payload 始终是不可信数据，不能直接变成 claim/EA。

---

## 5. 当前底层逻辑的具体漏洞

这些不是抽象问题，是代码里会破坏理论保证的点：

1. **closure 仍从 demo 读 capsule status**：demo 可重新标 completed，而 capsule 文件 hash 仍可能通过；
2. **lineage 的 dataset/code hash 来自 capsule 字段**：没有从当前数据/代码文件重算；
3. **signature 是 JSON**：没有身份/公钥/验签；
4. **maintenance.reclose 的输入绑定**：刚修了一个越界问题——demo/claim 必须位于 bundle 内，claim hash 必须匹配当前 lineage 节点；否则可以用另一套输入重闭合；
5. **自动 reclose 仍可能在漏边时给出虚假的 ready_for_resign**；
6. **bundle manifest 没有外部锚点**：攻击者可同时改 manifest 与文件；
7. **waitpoint secret 以 env/命令返回，可能泄漏**；signal 数据不证明执行；
8. **runtime job 在内存、无 auth**：重启/并发/越权都没有理论保证；
9. **Review Pack 没有 eval**：确定性检查不等于质量提升；
10. **前端是 SIM**：BRIEF/Review Pack 不能当作运行证据。

---

## 6. 什么条件下才可能出现“好效果”？

我认为至少要同时满足：

1. **范围窄**：先只覆盖结构化结果 claim（不是任意论文句子），让 `D` 有机会接近 `S`；
2. **边可测**：每条边有类型和 scope；对边覆盖率做审计，而不是假设完整；
3. **门禁唯一**：导出只有一个 reference monitor，浏览器/CLI/脚本不能绕过；
4. **签名可验**：signer 身份 + 公钥 + append-only 审计 + 外部锚点；
5. **处置精度可测**：`rerun/rewrite/recheck` 与人工判断对照，误报/漏报有数字；
6. **人因可接受**：签名摩擦不能高到让人直接绕过，也不能低到变成橡皮图章；
7. **维护成本有优势**：与全量重跑/人工 diff 对照，time-to-reclose 和 human minutes 真有下降；
8. **语义支持可校准**：claim×span×EA 的支持/反驳/不足有标注集和 κ，不把 LLM judge 当真理。

没有第 1–4 条，系统不能保证“旧导出被拦住”；没有第 5–7 条，不能保证“真的省事”；没有第 8 条，不能保证“结论正确”。

---

## 7. 理论上的“效果”应该怎么表述

### 可以说的

- 在声明依赖图上，变更传播是保守的；
- 在门禁被唯一强制执行时，stale + 无新签名会阻止导出；
- 在 recheck-only 且输入绑定正确时，reclose 可以安全地重跑 closure；
- 人签/bundle 提供了可追溯的交付记录；
- 我们的差异是“维护闭环”，不是“自动科研”。

### 不能说的

- “系统能保证科研结论正确”；
- “所有受影响内容都会被找到”（边覆盖不足）；
- “自动修复已完成”（只覆盖 recheck-only）；
- “旧导出绝对无法绕过”（没有 reference monitor）；
- “人签等于理解”；
- “RSI 已产生能力增益”。

---

## 8. 可证伪的验证计划

要判断是否“达到很好的效果”，至少需要：

1. **10–20 个真实/半真实变更案例**，包括数据、代码、引用、claim 文本、scope、图数据、外部任务失败；
2. **人工标注真实受影响集合**，计算 stale 召回/精度；
3. **与全量重跑、人工 diff、无门禁三组对照**，记录 time-to-reclose、human minutes、错误率、成本；
4. **对抗测试**：伪造签名、陈旧 manifest、越界 demo/claim、漏边、并发 reclosure、崩溃恢复；
5. **Review Pack 对照**：无 review / Loop 自检 / Review Pack；
6. **预先写 kill criteria**：如果维护计划不能优于人工 diff，或 false export allow 不为 0，则停止宣称“差异化完成”。

在这些数字出来之前，理论上的最诚实结论是：

> **它有潜力成为一个有用的“保守完整性层”，但当前还不是一个可证明有效的科研维护系统。**

---

## 9. 结论

这套设计的理论价值不在“模型更聪明”，而在于把科研失败模式变成可计算对象：

- 变更 → 依赖图 → stale；
- stale → 处置；
- 处置 → reclose 或阻断；
- reclose → closure；
- closure → 人签；
- 人签 → 不可变 bundle。

但它的保证是**条件性的**：

```text
完整声明图 + 唯一门禁 + 可验证签名 + 可测处置 + 真实维护基准
  → 可以显著降低旧证据被继续交付的风险
缺少任何一项
  → 容易退化为 stale 仪表盘或虚假安心
```

所以，后续设计应优先补“覆盖、门禁、签名、评估”，而不是继续加 Agent 或 UI。只要坚持这个边界，这项工作在理论上是可以站得住的；如果把它说成“自动科研”或“保证正确”，它在理论上立刻站不住。

## 10. 主要理论来源（用于区分定理与假设）

- Saltzer & Schroeder, *The Protection of Information in Computer Systems* (1975): complete mediation, least privilege, separation of privilege, fail-safe defaults. https://doi.org/10.1109/PROC.1975.9939
- Mokhov, Mitchell & Peyton Jones, *Build Systems à la Carte* (ICFP 2018): dependency tracking, early cutoff, minimality, rebuild strategies. https://www.microsoft.com/en-us/research/publication/build-systems-la-carte/
- Buneman, Khanna & Tan, *Why and Where: A Characterization of Data Provenance* (ICDT 2001): why/where provenance and provenance propagation. https://doi.org/10.1007/3-540-44503-X_20
- Parasuraman & Riley, *Humans and Automation: Use, Misuse, Disuse, Abuse* (1997): automation bias, overreliance and disuse. https://doi.org/10.1518/001872097778543886
- MDPI *From Trust in Automation to Trust in AI in Healthcare* (2025): a review connecting automation trust/bias to AI oversight. https://www.mdpi.com/2306-5354/12/10/1070
- 本地：`14-`/`36-`/`39-`/`42-` 的需求、市场与后端审计；`research/cortex-agent/AUDIT.md` 的 Anthropic/Cortex 对照。

这些来源支撑的是**原则与条件**，不是“我们的系统已经产生了效果”。效果仍需第 8 节的可证伪实验。

