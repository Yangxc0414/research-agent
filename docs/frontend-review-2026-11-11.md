# 前端系统复盘：Pages demo 与真实工作台（2026-11-11）

## 0. 复盘边界

- **对象**：「当前 demo」= `yangxc0414.github.io/research-agent/`，含 `/app/`（React 工作台的静态构建）与 `site/` 下 8 个独立静态子页；「真实前端」= `Wellspring-Agent` 产品工作台（`npm run build` + 本地 FastAPI runtime，8787）。
- **不做**：新增能力、改门禁语义、改数据流、改接口、合并仓库、重组架构。全部改进限于**解释层与呈现层**（文案、图例、术语、反馈、字阶、留白）。
- **基线**：本轮已修 `ClaimGateDialog` 的 claim 人工门与 `LineagePage` 的导读/图例/术语中文化，以下清单不重复计入。
- **证据口径**：行号均基于外层 `apps/web/src`（唯一源）与 `site/`；两树前端源码逐字节一致（`diff -rq` 0 差异，仅外层多一个空目录 `features/`）。

## 1. 事实基线：两者到底是不是两套前端

| 项目 | 当前 demo | 真实前端 |
| --- | --- | --- |
| 源码 | 同一份 `apps/web/src`（91 文件） | 同左，由外层 `scripts/build_release.py` 单向同步 |
| 构建 | `build:site`：`vite build --mode static --outDir ../../site/app`，`__STATIC_ONLY__=true`（`vite.config.ts:12`） | `build`：`vite build`，`__STATIC_ONLY__=false` |
| 后端 | `runtimeApi.ts:644` 所有 `/api` 硬抛 `runtime disabled in static build` | `vite.config.ts:16-23` 代理 `/api` 到 8787 |
| 数据 | 随包 JSON + localStorage | `liveThenSnapshot()` 优先 `/api`，失败回退快照（`runtimeApi.ts:676-683`） |
| 人工门 | 复制 CLI 命令 / 只读导入 claim.json / **DEMO 预览**（`ClaimGateDialog.tsx:157`） | 前两项保留；DEMO 预览被 tree-shake，`workspaceStore.ts:2040` 运行时拒绝 |
| 静态提示 | `StaticModeNotice` 可见 | `StaticModeNotice.tsx:8` 返回 null |
| 子页 | `site/demo`、`innovation`、`rsi`、`qoder`、`models`、`live`、`agent`、`docs` 为独立 HTML + 手写 JS | 产品仓库随包带同一份 `site/app`，但不部署 Pages |

**关键判断**：差异不是「两套逻辑」，而是**一个编译期开关 + 一组不属于工作台的静态展示页**。因此改进应落在共用源码的解释层，而不是为 demo 单独造一套文案。

### 1.1 三个维度的一致性与差异

| 维度 | 一致性（证据） | 差异（证据） |
| --- | --- | --- |
| **逻辑组织** | 共用入口 `main.tsx:7-13`、`staticAdapter.ts:50` 持久化、`gateCommands.ts:4-11` 门禁语义（浏览器不代签）、canonical 门禁口径 `G1=S3/G2=S4/S5b=S5c/G5=S16`（`site/index.html:569,606`）；`ClaimGateDialog` 两种构建都打开 | `__STATIC_ONLY__` 共 14 处分流：运行配置块隐藏（`ContextPanel.tsx:679,762,794,799`）、模型禁用（`ModelPicker.tsx:105`）、设置卡隐藏（`WorkspaceSettings.tsx:646,682`）、LiveRun 改判（`workspaceStore.ts:2796`）；静态多 DEMO 预览、产品明确拒绝 |
| **交互呈现** | 共用 31 个组件、同一 zustand store、同一套弹层/焦点/Esc 行为；`/app/` 与 `dist/` 仅 bundle 名不同 | 静态子页是独立 HTML，各自 localStorage（`site/live/live.js:241`、`site/models/models.js:100`）、无共享路由、不读写工作台状态；`/app/` 无 `sp-top` 外壳，其余子页有 |
| **信息表达** | `apps/web/public/*.json` 与 `site/app/*.json` 9/9 逐字节一致；共用「红=人工门 / 青=自动门 / 虚线=反馈」读图约定（`site/index.html:570`） | 同一「自进化」两套数据两套指标：工作台 `rsi-story.json`（`RsiStoryPanel.tsx:31-90`，EPISODES/LEASES/CLAIMS）vs `/rsi/` 的 `site/data/harness2.json + evolution.json`（RECURSION BUDGET R/P、CONFORMANCE、GENERATIONS）；`command-catalog.json` 在 `WorkspaceSettings.tsx:97`、`/qoder/` 手写表、`domain/commandCatalog.ts:27` 三处各说各话；静态事实有 6 种叫法 |

## 2. 四个维度的诊断口径

- **可解释性**：术语、状态值、数据来源、ID 首次出现时，用户能否不看源码就知道「这是什么」。
- **可读性**：层级是否分明、字号是否可辨、长串是否处理、密度是否可扫读。
- **使用习惯**：点击是否有可见反馈、指令是否可发现、不可操作项是否诚实标注、禁用态是否有原因。
- **视觉美观度**：字阶与留白是否统一、导读/图例是否复用同一组件、空态与隐藏块是否留下突兀空白。

## 3. 问题清单（按影响范围与优先级排序）

> 每项均注明**不改动**的边界；验收标准以可 grep / 可截图 / 可单测为准，不以「看起来更清楚」为准。

### P0 · 全站 / 跨页，直接造成「看不懂这些是啥」

| # | 影响范围 / 维度 | 现状问题（证据） | 期望效果 | 验收标准 |
| --- | --- | --- | --- | --- |
| **P0-1** | React 工作台 + 全部 Pages 子页 / 可解释性 | 首屏裸英文缩写无注解：`site/innovation/index.html:44`（EA/AUC/raw/event-count/provenance/pending）、`:184`（StepLedger/lease/MetaTracker/bound_claim/DataCite/H1–H4 十几连写）、`:96-110`（Q0/G0/G1/G2/S5b/G3/G5/EB/slots）、`site/rsi/index.html:156-159`（RECURSION BUDGET / R=4k P=3k / CONFORMANCE）、`site/models/index.html:87`（WIRED / CONFIG ONLY）、`site/live/index.html:44-47`（STATUS/QUEUE/RSI/SIGN + CHECKING/IDLE）、`site/agent/index.html:199-201`（RUN/EVIDENCE/EVOLUTION/CTX）、`site/index.html:253-254`（RunCapsule/EA/stale/fail-closed）；工作台侧 `ArtifactCard.tsx:73` 等 10 处英文卡片头、`RsiStoryPanel.tsx:69-82` 整屏英文 KPI | 建一份全站术语表（复用 `domain/lineageLabels.ts` 的「中文名 + 一句解释 + 英文代号」模式）；首次出现中英并列或 `title` 注解；Pages 子页首屏加「本页术语」折叠条；`innovation:184` 拆为「已实现 / 待验证 / 不宣称」三栏 | 对固定术语集（EA、claim、closure、span、RunCapsule、S5b/G5/Q0、MCP、RSI、fixture、SIM、STALE、SLOT、sealed、delegated、WIRED、CONFIG ONLY、UNTRUSTED、AUC、provenance）做静态扫描：首屏可见文本中裸缩写数为 0；每条有中文注解或 `title`；两种构建产物文案一致；`innovation:184` 不再是单段黑话连写 |
| **P0-2** | 工作台 + `/rsi/` `/demo/` / 可解释性 + 可读性 | 状态徽标直接渲染英文原值并着色，全站无统一图例：`ContextPanel.tsx:973` `gate.status.replaceAll("_"," ")`、`:1007`、`:1204`、`:1632`、`:1776`；`ArtifactCard.tsx:421-431` `BOUND/PENDING/LOCKED` 三态；`SettingsSections.tsx:343-344` `approved/denied/proposed`；`TopBar.tsx:110-114` `API · LOCAL / 演示数据 · 静态 / RUNTIME 已禁用` 三态变色；`site/rsi/index.html:418` 绿黄红 pill 配 `ok/warn/adopted/reverted` | 统一 `statusLabel()` 中文映射 + 一个可复用的 `LegendBar`（绿=通过、黄=待人工/需复核、红=阻断/失效）；每个出现状态色的区域紧邻一条图例；TopBar 三态改纯中文并说明「已连接 ≠ 会真实执行」 | `grep` 不到 `replaceAll("_"," ")`、`BOUND/PENDING/LOCKED`、`approved/denied` 等英文值直接渲染；5 个抽查区域（RUN 门禁、写作槽位、工具调用、顶栏、rsi 任务表）均可见中文图例；1440/1024 截图无文字重叠 |
| **P0-3** | 全站 / 可解释性 | 同一概念多套说法：静态事实 6 种叫法（`StaticModeNotice.tsx:11`、`TopBar.tsx:110`、`site/demo/index.html:2014`、`site/agent/index.html:41`、`site/innovation/index.html:29`、`site/index.html:198`）；门禁编号两套（`site/index.html:569,606` 的 `G1=S3/...` vs `site/demo/index.html:2345` 的 `G1(P2)/G2(P3)/S5b(P5)/G5(P7)`）；「自进化」两套数据两套指标（见 §1.1）；`site/index.html:217-226` glossary 只解释 5 个数字，未解释关键词 | 一个文案常量定义「静态演示模式 = 编译时禁用 runtime、数值来自快照、真实运行/签核/导出只在 CLI」；门禁映射单一事实源；每页注明「本页数据来源」，跨页同名概念用同一说法 | 6 处引用同一常量；门禁编号只有一种映射；`/app/` 与 `/rsi/` 各自可见数据来源说明；`site/index.html` glossary 扩为「数字 + 关键术语」两节；`scripts/check-site.mjs` 可加一条断言防止回退 |
| **P0-4** | Pages demo 子页（`/demo/` `/agent/`）+ React 输入框 / 使用习惯 | 点了没有可见结果：`site/demo/index.html:7728` `if(act==="toast"){ toast(...); return; }` 覆盖「导出已阻断 / 查看失败记录 / 标记复核 / 改写建议」等按钮；`site/agent/agent.js:2279` `default: toast("这个动作在静态预览中还没有接线。")`；`:2148-2155`「测试连接（SIM）」只延时换按钮文字；`:1932` `/help` 只弹一长串英文指令；`WelcomeHome.tsx:174` 与 `site/agent/index.html:186` 输入框提示有 `/` 指令却无清单 | 要么产生可见状态变化（切视图 / 展开详情 / 写入队列），要么显式标注「仅说明 / 静态预览不可用」并去掉按钮外观；未接线 action 隐藏或置灰；`/help` 与输入框旁提供中文指令清单，点击即填入 | 点击后 200ms 内有 DOM 可见变化或明确禁用态；源码中不再有 `toast("…还没接线")` 类兜底；指令清单每条有中文说明且可点击填入；Playwright 对 6 个原 toast-only 按钮逐一验证 |
| **P0-5** | 工作台运行卡 + `/qoder/` `/rsi/` / 可解释性 + 使用习惯 | CLI 命令与长 ID 裸摆：`ArtifactCard.tsx:566-597` / `:577-581` / `:618-623` 四段多行 `python -m research_agent ...` 含 `<IDEA-ID>`、`<run-dir>` 占位符，未说明「复制到本地终端、网页不会运行、占位符需替换」；`site/qoder/index.html:298-315` 一屏 6 个 `RUN-/MT-/RG-` ID + `S5_NOT_RUN/needs_human/blocked`；`site/rsi/index.html:287` 三段省略号命令与截断 SHA | 统一命令块组件：一句用途 + 「仅本地终端执行，本页不运行」 + 占位符标「需替换」 + 复制按钮；ID 前加中文标签并 `title` 给全值，附一句「这是一次历史回执，本页不可重放」 | 所有 `<pre>` 命令块四要素齐全；`<IDEA-ID>` 等占位符有可见标注；ID 均有中文标签与全值 `title`；不可点击的 ID 不伪装成按钮；单测覆盖命令块渲染契约 |

### P1 · 工作台主要区域，影响主路径理解

| # | 影响范围 / 维度 | 现状问题（证据） | 期望效果 | 验收标准 |
| --- | --- | --- | --- | --- |
| **P1-1** | 主对话区全部产物卡 / 可读性 | `ArtifactCard.tsx:73,102,129,157,200,278,324,421,497,674` 十处 `CardHead` 主标题为英文代号：`PLAN / RETRIEVAL`、`COVERAGE / SOURCES`、`GAP → HYPOTHESES`、`PROTOCOL / S4`、`RUN / … meta="EA SEALED"`、`WRITING / SLOT BINDING`、`TOOL CALL / MCP`；用户在主流程里看不到阶段中文名 | 中文主标题 + 英文代号降为副标小字；每张卡片首次出现补一句「这一阶段产出什么」 | 10 处 `CardHead` 中文主标覆盖率 100%；英文代号仍可见（保留 CLI 对照）；Playwright 抽 3 张卡片断言中文主标与说明可见 |
| **P1-2** | 上下文「自进化 / 治理」两个面板 / 可解释性 + 可读性 | `RsiStoryPanel.tsx:69-82,106,119,133,152,173,185,199` 全屏 `RSI STORY / LIVE LEDGER / EPISODES / APPROVED / REJECTED / LEASES / CONFIRMED / CLAIMS / ADMISSION TIMELINE / PREDICTION AUDIT / NEGATIVE RESULTS`；`GovernancePanel.tsx:46,60-76` `GOVERNANCE CHAIN / UNAVAILABLE / SPEC ↔ CHANGELOG / fresh / stale`；`ContextPanel.tsx:2100-2101` 直接挂载、无导览；静态构建下 `UNAVAILABLE` 必现（`runtimeApi.ts:644`） | 面板顶部 2–3 行中文导读（这是什么账本、数字代表什么、为何不能当能力结论）；KPI 标签与状态值中文映射；空态说明「为何不可用 + 需要什么才有数据」 | 两个面板首屏可见中文导读；所有 KPI 标签中文；`UNAVAILABLE` 空态含原因与恢复条件；不新增任何数据请求 |
| **P1-3** | 输入框 / 命令面板 / 使用习惯 | `WelcomeHome.tsx:174` placeholder 提到「使用 / 调用 Skill」但无可见指令清单；`site/agent/agent.js:1932` `/help` 返回 19 个英文指令名的 toast；命令面板（`⌘K`）与 `/` 指令表未联动 | 输入框旁「可用指令」折叠清单（中文说明 + 点击填入）；`/help` 打开该清单而非 toast；命令面板复用同一份指令数据 | 清单可见且每条有中文；点击条目填入输入框；`/help` 不再只弹 toast；`domain/commandCatalog.ts` 为唯一指令数据源 |
| **P1-4** | 运行卡 / 接入矩阵 / 自进化页 / 可读性 | 长串未处理：`ArtifactCard.tsx:500,516` `jobId / jobDir` 直接塞 `<code>`；`site/qoder/index.html:298-315` 6 个历史 ID；`site/rsi/index.html:454,488-491` `tree <12位>…`、`commit <7位>…`；均无标签、无全值、无「这是什么对象」 | 中文标签 + 缩短显示 + 悬停全值 + 一键复制（可复用 `LineagePage` 的 `CopyHash` 模式）；注明对象类型（运行 / 模型回合 / 委托结果 / 内容指纹 / 提交号） | 所有长串前有中文标签；`title` 含全值；截断串可复制；无标签长串数为 0；剪贴板不可用时展开全文 |

### P2 · 局部视觉与复用，提升整体一致性

| # | 影响范围 / 维度 | 现状问题（证据） | 期望效果 | 验收标准 |
| --- | --- | --- | --- | --- |
| **P2-1** | 全站字阶 / 视觉美观度 + 可读性 | `styles/*.css` 中 `calc(10px * var(--settings-font-scale))` 出现 **200 次**，另有 9.5px×11、9px×7、8.5px×1；`ContextPanel.tsx` 2435 行、31 组件，正文与标签几乎同字号，层级靠颜色而非字阶 | 正文基准提升到 11px（仍随 `--settings-font-scale` 缩放），标签类可保留 9.5–10px；标题与正文相差 ≥2px；长列表按语义分组加小标题（不重构组件） | 抽样 5 个高频面板，正文计算字号 ≥11px；标题/正文差值 ≥2px；1440 与 1024 截图无重叠、无截断；不改动 DOM 结构与数据流 |
| **P2-2** | 导读 / 图例组件 / 视觉美观度 + 一致性 | `LineagePage` 已有 `.lineage-guide` / `.lineage-legend`（`styles/lineage.css`），但主页 glossary、流程图图例、`site/qoder/index.html:158-163`、`site/innovation/index.html:199` 各写各的样式，视觉语言不统一 | 抽成共用 `GuideCard` / `LegendBar`（React 侧）与一份 Pages 共用样式类；新页面复用而非复制 | 至少 3 个高频页面复用同一组件/样式类；样式单点维护；不要求所有静态子页改造成 React |
| **P2-3** | 静态构建的隐藏块与空态 / 视觉美观度 + 使用习惯 | `ContextPanel.tsx:679,762,794,799` 与 `WorkspaceSettings.tsx:646,682` 在静态模式下直接隐藏运行配置块，页面留下无说明的空白；`ModelPicker.tsx:105-110` 仅显示「演示态」；`GovernancePanel.tsx:46` 英文空态 | 隐藏区域给一条统一的替代说明（「真实运行需本地 runtime；本页为静态预览」），禁用控件说明原因；空态不留突兀空白 | 静态构建下每个隐藏区域有可见替代说明或统一提示；不存在「看得见分组标题、看不见任何内容」的区域；产品构建下这些替代说明不出现 |

**每项均不改动**：功能意图、使用场景、门禁语义（浏览器不代签、默认拒绝、存算分离）、接口与数据结构、`__STATIC_ONLY__` 分流边界、现有 fixture 数值与负结果判定。

## 4. 已达标项（避免重复做）

- `ClaimGateDialog`：点击有确定面板、三条路径、DEMO 标记、导入校验、可撤销（本轮已做）。
- `LineagePage` / `LineageDag`：导读卡、三步指引、图例、术语单一事实源、中文阶段名、可复制哈希、只读警示条（本轮已做）。
- `site/index.html:217-226` 数字 glossary、`:265-270` 流程图图例、`:567-571` canonical 门禁卡片；`site/innovation/index.html:199`、`site/qoder/index.html:158-163` 门图例；`site/demo/index.html` 多张流程图图例。
- 两树前端源码与 `site/app` 产物逐字节一致；`test_release_integrity` 6/6；`npm run check` 21 单测通过。

## 5. 收敛判断

- 「用户看不明白这些是啥」的成因不是功能缺失，而是**解释层缺席**：术语、状态、数据来源、点击反馈四类信息没有随机器输出一起呈现。P0 五项做完即可消除该现象，且全部落在文案/图例/组件层面。
- P1 提升工作台主路径的可读性，P2 统一视觉语言；三者都不新增能力、不改门禁、不动数据流。
- **不建议**继续扩功能来「让页面看起来更饱满」：那会破坏「投影=愿景、实现=窄版」的诚实区分，也会重新引入演示数据被误读为真实结果的风险。
- 建议实施顺序：P0-1/2（术语与状态）→ P0-3（口径）→ P0-4/5（反馈与命令块）→ P1 → P2；每批以本表验收标准逐项核对，一次只改一个模块。
