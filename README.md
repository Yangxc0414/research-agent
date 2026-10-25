# Research Agent · Frontend Demo

Static-first research workbench deployed to GitHub Pages.

- Landing: https://yangxc0414.github.io/research-agent/
- Workbench: https://yangxc0414.github.io/research-agent/app/
- Innovation demo: https://yangxc0414.github.io/research-agent/innovation/

## What this repository is

This is the **frontend/deployment mirror** of the Research Agent project:

- `apps/web/` — Vite + React + TypeScript source for the workbench;
- `site/` — the deployable Pages root: landing page, `app/`, `demo/`, `models/`, `live/`, `innovation/`, docs and data snapshots;
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
