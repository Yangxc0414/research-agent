# Research Agent · Frontend Demo

Static-first research workbench deployed to GitHub Pages.

- Landing: https://yangxc0414.github.io/research-agent/
- Workbench: https://yangxc0414.github.io/research-agent/app/
- Innovation demo: https://yangxc0414.github.io/research-agent/innovation/

## What makes this different

四条可检验的工程差异，均可在工作台/创新演示里点出来：

1. **证据链而不是聊天记录** — 每个结论挂在 `SourceHit → Span → Claim(EA) → Closure` 链上；摘要-only 来源只作线索，永远不生成 span。
2. **人工门禁是设计，不是补丁** — 系统不自动签署 claim、不自动导出；G1/G2/S5b/G5 门禁在 UI 与 CLI 上同样生效，全自动只在作者写下的策略内委托运行。
3. **受治理自进化（lease-gated RSI）** — 自改进只能提案（pending）；准入要求 dry-run、public/hidden 回归与人工租约，负结果保留在账本里。
4. **图也有 provenance** — AstraDraw scene → SVG 带哈希 manifest 与审计；结果图不能脱离 EA 单独引用。

主项目包含 26 个带 SPEC 契约的模块与 107 个测试文件；本仓库只发布静态前端镜像。

## What this repository is

This is the **frontend/deployment mirror** of the Research Agent project:

- `apps/web/` — Vite + React + TypeScript source for the workbench;
- `site/` — the deployable Pages root: landing page, `app/`, `demo/`, `models/`, `live/`, `innovation/` and data snapshots;
- `demo/` — the legacy single-file research-run demo copied by `build-site.mjs`;
- `scripts/build-site.mjs` — assembles the static site;
- `.github/workflows/pages.yml` — builds the workbench in static mode and deploys `site/`.

It does **not** include the Python runtime, private data, `oss/` snapshots, or third-party source archives.

## Static boundary

`npm run build:site` builds with Vite mode `static`; `runtimeApi` then reads bundled snapshots and never requests `/api`. This keeps GitHub Pages free of 404/500 noise.

The workbench is still a **SIM / STATIC** demonstration:

- no real LLM call, tool execution, sandbox, or claim signature;
- no real retrieval from this frontend (OpenAlex is only available in the public site lab / local runtime);
- local state is stored in browser localStorage;
- evidence, closure, lease and self-evolution views are UI/control-plane demonstrations unless connected to the local runtime;
- no secret or API key is present in this repository.

The full project (backend, tests, design docs) lives outside this frontend mirror.

## Local preview

```bash
cd apps/web
npm ci
npm run typecheck
npm run build:site
cd ..
node scripts/build-site.mjs
python -m http.server 8000 --directory site
# open http://127.0.0.1:8000/
# workbench: http://127.0.0.1:8000/app/
```

## Deploy

Push to `main`; `.github/workflows/pages.yml` builds and uploads `site/` to GitHub Pages.

- `pull_request` runs the same build and `scripts/check-site.mjs` but does **not** deploy;
- `push` to `main` builds, checks the static artifact, uploads `site/`, then deploys;
- jobs have timeouts and separate concurrency groups for PR vs main;
- `scripts/check-site.mjs` verifies required Pages files, app asset references, and the static-runtime guard.

Repository Settings → Pages → Source must be set to **GitHub Actions**.

## Verification

- static build: no `/api` requests, no 4xx/5xx, no console errors;
- 1440 / 390: no horizontal overflow;
- typecheck and `build:site` pass.
