# 深层反思：我们不是在造“更会写论文的 Agent”

> 日期：2026-10-25  
> 性质：产品定位、底层模型与后续设计的反思，不是已完成能力清单。  
> 依据：本地 14/36/39/42、Cortex 对照审计、当前 `research_agent/` 与 `apps/web/` 代码、144 个后端测试、真实 ChemLab 闭合快照。  
> 结论先行：**我们的差异不在“生成”，而在“证据托管与变更维护”。** 如果继续用 Agent 数量、阶段数量、聊天体验来证明自己，差异会被市面产品迅速覆盖；真正需要补的是四个底层模型。

## 0. 一句话判断

市面上大多数科研 Agent 优化的是：

```text
问题 → 检索 → 想法 → 实验 → 写作 → 评审
```

我们当前真正有机会守住的，是这条链的**下半场**：

```text
已闭合的研究包
  → 数据/代码/协议/引用发生变化
  → 哪些 claim、图、槽位、closure、signature 失效
  → rerun / rewrite / recheck
  → 重新闭合
  → 人签
  → 旧导出继续被拦住
```

所以，更准确的产品定义不是“AI Scientist”，而是：

> **Research Evidence Maintenance Layer：让研究结论在证据变化后仍然可交付、可解释、可签署。**

这句话比“端到端科研”窄，但它是我们现有代码、测试与真实产物最能支撑的部分。

---

## 1. 市场位置：什么已经商品化，什么仍然稀缺

只按公开材料能确认的机制比较，不比较未复现的百分比。

| 能力 | 市场现状（2026-10 公开材料范围内） | 对我们意味着什么 |
| --- | --- | --- |
| 从问题生成论文/评审 | AI Scientist、Co-Scientist、DeepScientist 已强 | 不要正面竞争 |
| 生成时 claim→引用/数值/方法绑定 | ScientistOne/CoE、ARIS、中文证据链产品已有 | 这是入场券，不是主卖点 |
| 第三方论文事后审计 | ARIS/Anti-Autoresearch 已有 evidence ledger 与可定位报告 | 不能把“审计”当空白 |
| 局部编辑的非局部传播 | EditPropBench 已测量 | 不能把“失效传播”概念当首创 |
| 长时工作区/team/memory/GPU | Cortex 已有强工程实现 | 不要重造它的工作台 |
| 变更后的修复、重闭合、重签、导出门 | 公开材料中仍较少见；多数停在报告或手工操作 | **我们的真正机会** |

我们不应该把“证据链”三个字单独立成 novelty，因为绑定/审计已经商品化。我们真正要守的是：

> **把“变更传播”从一次性报告，变成受门禁约束的维护流程；把“修复”从改一句话，变成重新闭合与重新签署。**

---

## 2. 当前工作的真实成色

### 2.1 已经能支撑差异化的部分

- **Run-bound EA/claim**：S5 真实本地 run，生成 RunCapsule/EA；claim 只能引用 EA，不能凭空写“supported”；
- **Closure 事实校验**：已补 protocol/bibliography/result-figure 伴随文件检查，bibliography entries 重新哈希；真实 closed-loop 14 项检查、8 个 artifact refs；
- **不可变证据 bundle**：`closure.publish` 复制签名清单内全部证据，逐文件 sha256、fsync、原子 rename、禁止覆盖；`verify-bundle` 可发现篡改；
- **内容寻址 lineage**：dataset/code/run/EA/claim/figure/slots/closure/signature 的依赖图；
- **三类处置**：stale → `rerun / rewrite / recheck`，真实变更 2/6/7，导出 blocked；
- **本地 waitpoint**：外部任务 `create → signal → inbox/consume`，secret 只存 hash，不联网、不自动签名；
- **BRIEF / Review Pack**：只读状态摘要与 advisory 审阅收据；
- **受控重闭合**：`maintenance.plan` 生成维护计划；只有 recheck-only 才允许 `maintenance.reclose` 重跑 closure；rerun/rewrite 阻断，人签与 publish 仍在外层；
- **真实测试**：144 个后端测试通过；前端 typecheck/build/site 检查通过。

这些是“证据维护层”的真实骨架，不是 PPT。

### 2.2 仍然只是部分实现的

| 能力 | 现状 | 不能宣称什么 |
| --- | --- | --- |
| Closure | 结构检查；capsule status 仍可从 demo 读取；不是语义支持 | 不能称“结论被证明” |
| Lineage | dataset/code 哈希来自 capsule 字段，未从当前文件重算 | 不能称完全内容寻址 |
| Claim/签名 | 普通 JSON；没有 signer 身份/公钥/验签 | 不能称密码学签署 |
| Protocol | 当前存在 run 后冻结路径 | 不能称预注册 |
| S1→Claim | Claim 只引用 EA，没有 span 边 | 不能称文献句已进证据链 |
| 处置/重闭合 | 处置是计划；recheck-only 可自动重跑 closure，rerun/rewrite 仍阻断 | 不能称自动修复/自动签核 |
| Waitpoint | 只有本地原语，未接持久 job/agent loop | 不能称长任务自动恢复 |
| Runtime | 内存 job、无 auth、单 worker | 不能称生产运行时 |
| RSI | 控制面/两个旋钮；hidden 不 sealed | 不能称能力自进化 |
| Review Pack | 确定性检查，无计分收益证据 | 不能称质量提升 |
| 前端 | 静态 SIM 工作台 | 不能把 SIM 当 LIVE |

**结论：我们已经有一个真实的“证据维护原型”，但还不是一个完成维护闭环的产品。** 如果现在对外宣称“差异化已经完成”，是不诚实的。

---

## 3. 四个底层模型必须改

这一节是最重要的部分。后续不应该再加 Agent，而应该把四个模型做硬。

### 3.1 证据模型：从“字段引用”到“可寻址、可判定、可放弃”

当前 claim 的对象太薄：`ClaimRecord` 只有 statement/scope/status/human_reason/evidence_refs；closure 只检查 ID/哈希/槽位。真实科研需要：

```text
Claim
  id, statement, scope, conditions
  support_refs: [SupportVerdict]
  status: draft | proposed | supported | contested | underdetermined |
          retired | reopened
  signer, signed_at
SupportVerdict
  claim_id, evidence_ref, relation: supports | contradicts | insufficient
  span/offset, method, reviewer, confidence
```

底层设计要补：

1. **S1→Claim 显式边**：文献句必须能指到 source version + span + offset；不是只引用 EA。
2. **SupportVerdict + Abstention**：支持/反驳/不足是三个不同状态；不能把“找不到证据”写成 supported。
3. **句子级映射**：稿件句子/段落 → claim/span/EA；否则只能维护 5 个大槽位，无法只重写受影响段落。
4. **条件化 claim**：scope/conditions/negative controls 必须和 claim 一起被签署，禁止从“设置 A 下 +3%”外推成“普遍 +3%”。
5. **raw evidence 保留**：任何总结/压缩都不能覆盖原始 span、页码、offset、artifact hash；压缩只能生成派生视图。

**不变量**：没有可定位证据，不得创建 supported claim；没有 SupportVerdict，不得进入稿件槽位；摘要-only 只能作为线索。

### 3.2 权限模型：从“文件里的 status”到“外部 Authority Kernel”

当前最大信任漏洞不是算法，而是权限：

- Claim/signature 是普通 JSON；任何能写目录的人都能伪造；
- Closure 仍可从 demo 读 capsule status；
- Protocol 存在 run 后再冻结；
- Approval 类能力如果由 Agent 可写文件承载，就不是权限边界。

底层设计应该有一个**独立的 Authority Kernel**：

```text
Agent / UI / CLI → propose（只能产生 proposal）
Authority Kernel → decide（签名、门禁、身份、租约）
Execution Plane → execute（只执行已授权动作）
Audit Log → append-only events（谁、何时、对什么哈希做了什么）
```

关键规则：

1. **模型只能提议，不能写 Claim/EA/gate/signature/export**；
2. Claim 必须有 signer 身份 + 对 canonical payload 的签名 + 时间 + scope；
3. Closure 必须从真实 capsule/EA 文件读取状态，不能信 demo 内嵌字段；
4. Run 前必须校验冻结 ProtocolCard；如果暂不做，就把对象改名，停止使用“预注册”；
5. 人工门失败的异常必须 fail closed，不允许 prompt-level “请批准”；
6. 签名/审批记录 append-only；撤销、过期、替代都留痕。

**不变量**：没有当前签名，不得导出；过期/失效签名不得复用；Agent 不得修改自己的授权记录。

### 3.3 变更模型：从“stale 报告”到“可执行维护协议”

我们已经把 stale 映射为 `rerun/rewrite/recheck`，但这仍是**按 kind 的启发式分类**。下一步需要：

```text
ChangeSet
  id, base_bundle, head_bundle, actor, reason, created_at
  changes: [{kind, target, before_hash, after_hash, severity}]

MaintenancePlan
  change_id
  items: [{action: rerun|rewrite|recheck, node_id, why, owner, gate}]
  export_blocked_until: [closure_id, signature_id]
  rollback: ...
```

底层要补：

1. **显式 ChangeSet**：不要只靠 baseline/current 哈希 diff；要记录“为什么改、谁改、改了什么”。
2. **选择性传播**：区分“必然失效”“需要复核”“不受影响”，不能全量报红；当前 `impact` 已做依赖传播，但还需语义边界。
3. **可执行重闭合**：ChangeSet → 新 run/EA → 重绑 slots → closure → sign；每一步幂等、可恢复、可回滚。
4. **版本化 bundle**：旧版、新版、失败版都保留；不能覆盖签名包。
5. **处置策略按变更类**：数据/代码变化通常 rerun；claim 文本变化通常 recheck + rewrite；引用撤稿通常 recheck + rewrite citation slot；图数据变化通常 rewrite + reclose。
6. **可解释的阻断**：给用户看“哪一条 claim、哪一张图、哪一句、为什么、下一步找谁”，而不是只给 14 个 stale 节点。

**不变量**：旧签名不得被复用；旧导出不得覆盖；任何 reclosure 必须绑定 ChangeSet；处置分类必须可审计、可回放。

### 3.4 运行时模型：从“内存 demo”到“可恢复执行”

当前 runtime 是本地原型：job 在内存、无 auth、单 worker；waitpoint 只是原语。底层应该改为：

```text
API / SSE / CLI
  ↓
Auth + policy (token, scope, deny by default)
  ↓
Durable store (SQLite 起步；Postgres 部署)
  - jobs(id, state, attempt, idempotency_key, timeout)
  - events(seq, type, payload, hash)
  - waitpoints / wakes / deliveries
  - artifacts (content-addressed)
  ↓
Worker(s) → adapters (retrieval/run/figure/LLM)
  ↓
Evidence plane (authority kernel) ← 只读/不可由 worker 写
```

关键规则：

1. job 状态机 `queued/running/succeeded/failed/cancelled`，有 timeout、重试、cancel、幂等键；
2. SSE 从持久事件表读，不依赖内存；
3. waitpoint 的 `inbox/consume` 接回 job resume，并保留“外部 data 不可信”的边界；
4. 浏览器只读/发起本地任务，不提供 claim/sign/approve 端点；
5. 存储迁移：JSON 快照可继续做导出，但主状态不能继续散落在多个 JSON；
6. 观测：token/成本/延迟/失败注入/artifact GC 都是一等指标。

**不变量**：进程崩溃后可恢复；重复 signal/consume 不重复产生副作用；模型 loop 无权写证据/授权记录。

---

## 4. 产品层：把“维护”做成一个清晰入口

### 4.1 不要继续做的东西

- 更多 Agent 人格/团队层级；
- 更多阶段时间轴；
- 通用聊天/搜索界面；
- 只换皮不改变对象的前端面板；
- 没有 eval 的“自进化”；
- 把 fixture/SIM 写成 live。

### 4.2 应该做的唯一入口：Change Review

一个页面/命令即可：

```text
Evidence Change Review
  [What changed]  dataset v3 / code commit / citation retracted
  [What is blocked] 1 claim / 2 slots / 1 figure / export
  [What to do] 2 rerun / 6 rewrite / 7 recheck
  [Next step] rerun S5 → rebind → reclose → re-sign
  [Proof] old/new hashes, bundle, signature, impact report
```

这条页面比“再做一个聊天框”更能让人记住产品，也更适合答辩：**系统在证据坏掉时比人更早发现，并且拒绝继续交付。**

### 4.3 BRIEF 的定位

BRIEF 不是 board，也不是证据；它只回答“新会话先读什么”：

- mission、stage、blockers、next、claim/closure、last review；
- 可复制 Markdown；
- 不写 claim/EA，不改 gate。

下一步应将它落成磁盘上的 `STATUS.md` / `decisions`，并让 Change Review 引用，而不是只停留在内存摘要。

---

## 5. 评估：没有分数，就没有差异化

### 5.1 先做 baseline

10–20 个 golden task，覆盖：

- 正常闭合；
- 数据集/代码变更；
- 引用撤稿；
- claim 文本修改；
- 图数据变化；
- 外部 job 完成/失败；
- 恶意篡改；
- 重跑失败/超时。

每个任务记录：

```text
completion / span-only / EA-claim / closure / export blocked
time / cost / human minutes / errors
process compliance
```

### 5.2 必须做的对照

1. **无维护 vs 全量重跑 vs 我们的 selective maintenance**；
2. **无 Review Pack vs Loop 自检 vs Review Pack**；
3. **旧 closure 复用 vs 强制 reclosure**；
4. **人工 diff vs dispositions**；
5. **签名篡改/过期/伪造**。

### 5.3 核心指标

- **False export allow**：stale/tampered 情况下仍导出，目标为 0；
- **Maintenance recall/precision**：受影响对象召回、误报；
- **Time to reclose**：从变更到重新可导出的时间；
- **Human minutes**：人工修复时间；
- **Cost/tokens**：重跑与审阅成本；
- **Claim support precision/recall/abstention**：语义支持评估，必须人工标注；
- **Rep-to-rep variance**：不能只看单次 demo。

没有这些数字，就不要说“比市面更好”；只能说“方向不同”。

---

## 6. 12 周优先级

| 阶段 | 周 | 重点 | 验收 |
| --- | --- | --- | --- |
| A. 信任边界 | 1–2 | closure 读真实 capsule/EA；signer 身份/验签；protocol 前置 | 篡改/伪造/过期测试全部阻断 |
| B. ChangeSet + reclosure | 3–5 | 显式 ChangeSet；执行 rerun/rewrite/recheck；版本化 bundle | 3 个真实变更端到端重闭合；旧导出保持 blocked |
| C. 句子级证据 | 6–7 | S1 span→claim；claim→句子；SupportVerdict/abstention | 受影响段落召回 ≥80%，误报 ≤20% |
| D. 运行时 | 8–9 | job 持久化、worker 恢复、waitpoint resume、SSE | 崩溃恢复、重复 signal、cancel、timeout 测试 |
| E. 评估与产品 | 10–12 | MaintenanceBench、Change Review UI、真实案例 | 与全量重跑/人工 diff 对照，报告时间/错误/成本 |

**不要**在第 1–12 周启动“更多 Agent/团队/RSI 能力增益”；那些只会稀释当前差异。

---

## 7. 可宣称与不可宣称

可以说：

> 我们在做一个科研证据的变更维护层：把 claim、EA、图、槽位、closure 与 signature 做成内容寻址对象；当数据/代码/引用变化时，系统传播失效、给出 rerun/rewrite/recheck 处置，并在重新闭合与人工签署前拒绝导出。公开材料范围内，这一组合仍较少见。

不能说：

- “首个/唯一/无人做过”；
- “自动修复已完成”（只覆盖 recheck-only 的 closure 重跑；rerun/rewrite/签核仍手动）；
- “零幻觉/可投稿/同行评审级”；
- “RSI 已实现能力增益”；
- “密码学签名已完成”（目前是 JSON signature）；
- “真实科研可用”（S1 仍是小语料；runtime 仍是原型）。

诚实不是减分项。**把边界写清楚，反而让差异更可信。**

---

## 8. Kill criteria 与风险

- 如果 10 个真实变更案例中，处置分类不能稳定优于“全量重跑/人工 diff”，则重新评估产品楔子；
- 如果 signer/closure 仍可被手写文件绕过，不能对外讲“治理”；
- 如果 S1 不能接入真实全文，维护层只能覆盖结果臂，不是完整科研维护；
- 如果 CoE/ARIS 等快速补齐 repair/reclosure，我们的优势会收窄，必须靠可测的 reclosure 执行与集成速度；
- 如果 UI 继续增加面板但不减少人工修复时间，停止改 UI；
- 如果没有 golden eval，任何“更好”的说法都只是叙事。

---

## 9. 结论

我们最值得保留的不是“13 个模块”“18 个阶段”或“多智能体工作台”，而是：

> **研究结论的托管权**：证据在哪里、谁签过、什么时候失效、重新闭合前不允许导出。

这条路的产品形态是 **Evidence Change Review + signed bundle + reclosure**；技术形态是 **evidence graph + authority kernel + change protocol + durable runtime**；研究形态是 **MaintenanceBench + SupportVerdict/abstention + 可测的修复时间/错误率**。

如果只能做一件事：先把“变更 → 处置 → 重闭合 → 人签 → 导出”做成一条能跑、能失败、能审计的真实链路。其他功能都围绕它服务。

理论层反思：[THEORY-REFLECTION.md](THEORY-REFLECTION.md)（声明依赖图 vs 语义依赖图、reference monitor、维护收益模型与可证伪条件）。

API 接入现状：[API-INTEGRATION.md](API-INTEGRATION.md)。
