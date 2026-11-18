# API 接入现状：一条真实的本地闭环

> 日期：2026-10-25  
> 目标：不是宣称“完整科研 Agent 已可用”，而是验证 **前端 → runtime HTTP API → 本地 pipeline → artifacts → 前端** 能真实跑通。  
> 结论：**这条窄链路已经跑通；主聊天/自动运行/模型科研流程仍未接 API。**

## 1. 已接通的部分

```text
Browser (RuntimeSettingsPage)
  → GET  /api/health
  → POST /api/runs
  → GET  /api/runs/{job_id}
  → GET  /api/runs/{job_id}/artifacts
  → artifact links (svg/json)
```

实现位置：

- 后端：`research_agent/runtime/app.py` 的 `/api/health`、`/api/runs`、`/api/runs/{id}`、`/api/runs/{id}/artifacts`；
- 前端：[runtimeApi.ts](file:///D:/Users/20691/Desktop/毕业设计/apps/web/src/adapters/runtimeApi.ts) 新增 `createRun/getRun/loadRunArtifacts/runtimeUrl`；
- UI：[WorkspaceSettings.tsx](file:///D:/Users/20691/Desktop/毕业设计/apps/web/src/components/settings/WorkspaceSettings.tsx) 的“本地任务 API”卡片；
- 静态 Pages：`__STATIC_ONLY__` 下隐藏运行按钮，避免把静态站伪装成 live；
- 测试：[test_runtime_api.py](file:///D:/Users/20691/Desktop/毕业设计/tests/test_runtime_api.py) 通过 `TestClient` 跑 health → POST run → poll → artifacts。

## 2. 实测结果

### 后端 HTTP

```text
GET /api/health → 200, human_sign=false, rsi_read_only=true, real_corpus=true
POST /api/runs → 202 JOB-...
poll → completed, 18 events
GET artifacts → 13 个产物
```

示例产物：`demo.json`、`experiment.json`、`figure.manifest.json`、`figure.svg`、`paper.json`、`run/ea.json`、`run/run-capsule.json`。

### 前端

- RuntimeSettingsPage 显示 `CONNECTED`；
- 点击“运行 ChemLab pipeline”后，真实 runtime job 完成；
- 前端显示 job/status/fixture/events/run 与 artifact 链接；
- 无 console error；
- 截图：`docs/frontend-audit/291-runtime-api-artifacts-1440.png`。

### 测试与构建

- 后端：**144/144 tests**；
- 前端：typecheck / build / build:site / `scripts/check-site.mjs`；
- 静态模式不显示运行卡片，避免 API 不可用时误导用户。

## 3. 这条链路“能用”的含义

它能证明：

- 前端可以真实调用本地 runtime，而不是只读静态快照；
- job 生命周期、artifacts 列表和下载链接可用；
- 运行结果明确标注 `fixture_mode`、warnings 和 `needs_human`，没有伪造 claim；
- 本地 pipeline 可以真实跑通，且不需要先把系统伪装成云端服务。

它不能证明：

- 主聊天/自动阶段已经接 runtime；
- 模型 API 已经接进 literature/idea/experiment/paper；
- runtime job 在重启后仍然存在；
- 有 auth/多租户/队列持久化/生产部署；
- closure/sign/maintenance 已通过 HTTP 暴露或由浏览器执行；
- 系统能辅助真实科研。

## 4. 下一步：把“完整闭环”接到 API

按优先级：

1. **主流程接 API**：`sendMessage` / 自动运行提交 `/api/runs`，用 SSE 渲染事件；不要再用 timer 模拟。
2. **持久化 runtime**：SQLite/Postgres 存 job/events，支持重启恢复、cancel、idempotency；加本地 token/auth。
3. **模型网关接 typed tools**：S1 query planner、S2/S3 候选、S8–S12 草稿只生成 proposal；claim/EA/gate 不可写。
4. **真实全文 S1**：PDF/HTML + offset；当前 OpenAlex 摘要不能生成 span。
5. **maintenance/closure HTTP**：只读 lineage/maintenance 查询；sign/publish 继续留在 CLI/Authority Kernel，不暴露给浏览器。
6. **评估**：用 API 跑 golden tasks 和 maintenance cases，测 false export allow、time-to-reclose、human minutes。

## 5. 框架反思

这次接入揭示了整体架构的真实形状：

```text
静态工作台（演示层）
  └─ runtimeApi（只读设置 + 本地 pipeline 调用）
       └─ runtime（内存 job / artifacts / SSE）
            └─ pipeline（确定性模块 + 本地 run）
                 └─ evidence plane（closure/lineage/maintenance，仍主要走 CLI）
```

问题不在“有没有 API”，而在 **API 只覆盖了执行入口，没有覆盖主交互和证据治理**：

- 主聊天仍是本地 reducer；
- closure/sign/maintenance 仍是 CLI；
- runtime 没有持久化与鉴权；
- 模型 API 没有进入研究流程。

因此，当前最准确的状态是：

> **“本地 pipeline API 已经可用；整体研究 Agent API 还没有完成。”**

下一步应先把主流程和持久化接上，再把模型作为 typed tool 接进 loop；不要为了“看起来能聊天”直接在前面加一个通用 LLM 对话框，那会绕过我们已经建立的证据边界。
