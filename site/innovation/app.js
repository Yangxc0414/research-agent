const ACT_MS = 6200;
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const MODULES = {
  literature: { label: "文献调研", kind: "literature" },
  idea: { label: "假设收敛", kind: "idea" },
  experiment: { label: "实验设计", kind: "experiment" },
  figure: { label: "科研绘图", kind: "figure" },
  paper: { label: "论文契约", kind: "paper" },
  grant: { label: "基金申报", kind: "grant" }
};
const ORDER = ["literature", "idea", "experiment", "figure", "paper", "grant"];
const ACTS = [
  {
    key: "spec", name: "契约", sub: "SPEC / MODULE", title: "先写契约，再写代码。",
    noteTitle: "最小的可演进单元",
    noteBody: "每个子智能体都有 SPEC.md。改行为先改契约，再用 CLI 做最小更新；正文与未涉及字段保持不动。",
    noteFact: "26", noteFactLabel: "SPEC · 107 TESTS", tags: ["SPEC", "minimal diff", "changelog"]
  },
  {
    key: "evidence", name: "证据", sub: "SPAN / COVERAGE", title: "证据不是聊天记录。",
    noteTitle: "摘要不是证据",
    noteBody: "检索、全文、句级 span、覆盖回执分开记录；没有全文就不能生成 span，更不能创建 Claim。",
    noteFact: "0", noteFactLabel: "claims from S1", tags: ["QueryPlan", "Span", "CoverageReceipt"]
  },
  {
    key: "figure", name: "图", sub: "SVG / PROVENANCE", title: "图也要有 provenance。",
    noteTitle: "先审计，再交付",
    noteBody: "AstraDraw 负责 scene→SVG；我们审计 XML、ID、文本、外部引用和 aria，并把哈希写进 manifest。",
    noteFact: "PASS", noteFactLabel: "SVG AUDIT", tags: ["scene hash", "svg hash", "no external"]
  },
  {
    key: "paper", name: "稿件", sub: "SLOT / GATE", title: "写作可以并行，结果不能抢跑。",
    noteTitle: "结果槽保持 pending",
    noteBody: "论文和基金只产骨架。没有 EA/Claim，结果槽不填；G5 导出保持 blocked，示意图不能绑成结果图。",
    noteFact: "5", noteFactLabel: "PENDING SLOTS", tags: ["PaperContract", "G3", "G5 blocked"]
  },
  {
    key: "boundary", name: "边界", sub: "CLAIM / NEXT", title: "不宣称“通用 AI 科学家”。",
    noteTitle: "把不能说的说清楚",
    noteBody: "五幕演示本体是 fixture、零 API。模型接线已在本地 runtime 实测：S1 规划器与 S2–S3 提案器经网关真实调用而门禁不减，见下方 LIVE WIRING 一节。",
    noteFact: "0", noteFactLabel: "API CALLS", tags: ["fixture acts", "live wiring ✓", "H1–H4"]
  }
];
const CHECK_LABELS = {
  root: "root svg", size: "width / height / viewBox", ids_unique: "unique ids",
  text_count: "text nodes", role_img: "role=img", labelled: "aria-labelledby",
  has_title: "title", has_desc: "desc", aria_targets: "aria targets"
};

let state = {
  data: null,
  specs: [],
  act: 0,
  playing: false,
  elapsed: 0,
  startedAt: 0,
  raf: null,
  autoTimer: null,
  presenting: false
};

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
const available = () => ORDER.filter((id) => id !== "grant" || state.data?.modules?.grant);
const statusOf = (id) => state.data?.modules?.[id]?.status || "not_run";
const specOf = (id) => state.specs.find((spec) => spec.id === id);
const moduleMeta = (id) => MODULES[id] || { label: id, kind: id };

function renderRail() {
  $("act-rail").innerHTML = ACTS.map((act, index) => `<button type="button" class="act-btn ${state.act === index ? "is-on" : ""} ${index < state.act ? "is-done" : ""}" data-act="${index}" aria-current="${state.act === index ? "step" : "false"}">
    <span class="act-no">0${index + 1}</span>
    <span><b class="act-name">${esc(act.name)}</b><span class="act-sub">${esc(act.sub)}</span></span>
    <span class="act-mark" aria-hidden="true"></span>
  </button>`).join("");
}

function noteFor(index) {
  const act = ACTS[index];
  return `<span class="note-kicker">WHY IT MATTERS</span><b class="note-title">${esc(act.noteTitle)}</b><p class="note-body">${esc(act.noteBody)}</p>
    <div class="note-tags">${act.tags.map((tag) => `<span class="note-tag">${esc(tag)}</span>`).join("")}</div>
    <div class="note-fact"><b>${esc(act.noteFact)}</b><span>${esc(act.noteFactLabel)}</span></div>`;
}

function specAct() {
  const ids = available();
  return `<div class="act-head"><p class="eyebrow">ACT 01 / SPEC</p><h2>${esc(ACTS[0].title)}</h2><p>六模块同构：输入、输出、门禁、不变量、实现边界都写在 Markdown 里；代码读取版本，CLI 只改指定字段。</p></div>
    <div class="spec-grid">${ids.map((id) => `<article class="spec-card" data-kind="${moduleMeta(id).kind}"><b>${esc(moduleMeta(id).label)}</b><small>${esc(specOf(id)?.stage || "")} · v${esc(specOf(id)?.version || state.data.spec_versions?.[id] || "—")}</small><em>${esc(statusOf(id))}</em></article>`).join("")}</div>
    <div class="spec-console"><span class="prompt">$</span> python -m research_agent spec update figure \\
  --version 0.1.1 --status pilot \\
  --changelog "最小改进：增加 SVG 审计"
<span class="prompt">→</span> body preserved · changelog appended · no cross-module edit</div>
    <div class="spec-points"><span>SPEC = single source</span><span>最小的 diff</span><span>version / changelog</span><span>tests first</span></div>`;
}

function evidenceAct() {
  const lit = state.data.modules.literature || {};
  const coverage = lit.coverage || {};
  const spans = (lit.spans || []).slice(0, 3);
  return `<div class="act-head"><p class="eyebrow">ACT 02 / EVIDENCE</p><h2>${esc(ACTS[1].title)}</h2><p>检索计划、来源命中、全文读取、句级 span 和覆盖缺口分开记录。摘要-only 只能作为线索，不能成为证据。</p></div>
    <div class="metric-row">
      <div class="metric"><b data-count="${coverage.sources_found ?? 0}">0</b><span>SOURCES FOUND</span><em>${coverage.sources_read ?? 0} full texts read</em></div>
      <div class="metric"><b data-count="${coverage.spans_extracted ?? 0}">0</b><span>SPANS EXTRACTED</span><em>sentence-level anchors</em></div>
      <div class="metric"><b data-count="${(coverage.gaps || []).length}">0</b><span>COVERAGE GAPS</span><em>reported, not hidden</em></div>
    </div>
    <div class="flow-line"><span class="flow-step">QueryPlan</span><span class="flow-arrow">→</span><span class="flow-step">SourceHit</span><span class="flow-arrow">→</span><span class="flow-step">full text</span><span class="flow-arrow">→</span><span class="flow-step">Span</span><span class="flow-arrow">→</span><span class="flow-step">CoverageReceipt</span></div>
    <div class="span-stack">${spans.map((span) => `<div class="span-item"><code>${esc(span.span_id)} · ${esc(span.section)}</code>${esc(span.text)}</div>`).join("") || `<div class="span-item">没有 span。先补全文。</div>`}</div>
    <div class="gap-line">${(coverage.gaps || []).map((gap) => `<span class="gap-chip">${esc(gap.code)}</span>`).join("") || `<span class="gap-chip">no gap reported</span>`}</div>`;
}

function figureAct() {
  const figure = state.data.modules.figure || {};
  const audit = figure.audit || {};
  const checks = Object.entries(audit.checks || {}).filter(([key, value]) => typeof value === "boolean");
  return `<div class="act-head"><p class="eyebrow">ACT 03 / SVG</p><h2>${esc(ACTS[2].title)}</h2><p>scene 由我们的 FigureAgent 生成，AstraDraw 渲染成 SVG；交付前必须通过可访问性、安全与文本检查。</p></div>
    <div class="figure-showcase"><img src="data/figure.svg" alt="研究运行时模块关系示意图；示意图，不是实验结果" /></div>
    <div class="audit-list">${checks.map(([key, value]) => `<div class="audit-row"><span class="audit-tick">${value ? "✓" : "×"}</span><span>${esc(CHECK_LABELS[key] || key)}</span></div>`).join("")}</div>
    <div class="hash-line"><span>SCENE ${esc((figure.manifest?.scene_sha256 || "").slice(0, 18))}…</span><span>SVG ${esc((figure.manifest?.svg_sha256 || "").slice(0, 18))}…</span><span>SCHEMATIC</span></div>`;
}

function paperAct() {
  const paper = state.data.modules.paper || {};
  const grant = state.data.modules.grant;
  const g5 = (state.data.gates || []).find((gate) => gate.gate === "G5") || {};
  return `<div class="act-head"><p class="eyebrow">ACT 04 / SLOTS + GATES</p><h2>${esc(ACTS[3].title)}</h2><p>论文与基金共享同一套 Evidence 约束：方法/结构可以先写，结果槽必须等 EA；示意图不能被冒充成结果图。</p></div>
    <div class="slot-grid">${(paper.slots || []).map((slot) => `<div class="slot-card"><b>${esc(slot.slot_id)}</b><span>${esc(slot.section)} · ${esc(slot.required_evidence)}</span><span class="slot-pill">${esc(slot.status)}</span></div>`).join("")}</div>
    <div class="track-grid">
      <div class="track-card"><span class="mono">PAPER TRACK</span><h3>${esc(paper.profile?.venue_type || "论文契约")}</h3><p>${esc(paper.profile?.citation_style || "GB/T 7714")} · ${(paper.sections || []).length} sections · 0 claims</p></div>
      <div class="track-card"><span class="mono">GRANT TRACK</span><h3>${grant ? esc(grant.scheme.toUpperCase()) : "未生成"}</h3><p>${grant ? `${(grant.modules || []).length} modules · ${(grant.compliance || []).length} compliance checks` : "用 --grant nsfc 生成基金骨架"}</p></div>
    </div>
    <div class="gate-banner"><span>G5 EXPORT · ${esc(g5.status || "blocked")}</span><b>${esc(g5.reason || "no EA/Closure")}</b></div>`;
}

function boundaryAct() {
  const specCount = state.specs.length || 6;
  return `<div class="act-head"><p class="eyebrow">ACT 05 / BOUNDARY</p><h2>${esc(ACTS[4].title)}</h2><p>这一页不把 fixture 说成实验，也不把“架构更清楚”说成“科研效果更好”。能证明的和不能证明的分开写。</p></div>
    <div class="boundary-grid">
      <div class="boundary-card"><b>不是通用 AI 科学家</b><p>机器负责检索、草稿、图、核验；科学决策、实验安全、署名与责任在人。</p></div>
      <div class="boundary-card"><b>不是效果论文</b><p>当前没有真实检索、run/EA、用户研究；不引用任何外部效果数字。</p></div>
      <div class="boundary-card"><b>可检验的工程差异</b><p>${specCount} 个 SPEC、57 个测试、SVG audit、结果槽阻断；这些都能在代码里找到。</p></div>
      <div class="boundary-card"><b>下一轮</b><p>OpenAlex adapter → EA/Run 账本 → 真实模板 → 5–8 人可用性测试。</p></div>
    </div>
    <div class="advantage-list">
      <div class="advantage-row"><b>SPEC</b><span>模块先有契约，改一个模块不必理解全部代码</span><em>implemented</em></div>
      <div class="advantage-row"><b>ARTIFACT</b><span>模块交换 artifact，不共享聊天上下文</span><em>implemented</em></div>
      <div class="advantage-row"><b>SVG</b><span>scene / svg / manifest / audit 一体</span><em>implemented</em></div>
      <div class="advantage-row"><b>BOUNDARY</b><span>结果槽 pending，G5 导出阻断</span><em>implemented</em></div>
      <div class="advantage-row"><b>RSI</b><span>StepLedger / policy / lease / MetaTracker；真实 evaluator 未接</span><em>control plane</em></div>
    </div>`;
}

const RENDERERS = [specAct, evidenceAct, figureAct, paperAct, boundaryAct];

function animateCounts(root) {
  root.querySelectorAll("[data-count]").forEach((el) => {
    const target = Number(el.dataset.count);
    if (!Number.isFinite(target) || REDUCED) { el.textContent = String(target || 0); return; }
    const start = performance.now();
    const run = (now) => {
      const p = Math.min(1, (now - start) / 520);
      el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(run);
    };
    requestAnimationFrame(run);
  });
}

function renderAct(index, animate = true) {
  state.act = Math.max(0, Math.min(ACTS.length - 1, index));
  const act = ACTS[state.act];
  $("stage-act-label").textContent = `0${state.act + 1} / 05`;
  $("stage-title").textContent = act.title;
  const canvas = $("act-canvas");
  if (!state.data) {
    canvas.innerHTML = `<div class="act-head"><p class="eyebrow">FIXTURE NOT LOADED</p><h2>先运行 fixture pipeline。</h2><p>从项目根目录运行 <code>python -m research_agent pipeline run ...</code>，再启动静态服务器。当前页面不会调用 API。</p></div>`;
  } else {
    canvas.innerHTML = RENDERERS[state.act]();
    if (animate) {
      canvas.classList.remove("is-enter");
      void canvas.offsetWidth;
      canvas.classList.add("is-enter");
    }
    animateCounts(canvas);
  }
  $("act-note").innerHTML = noteFor(state.act);
  renderRail();
  setProgress(0);
  setSource();
}

function setSource() {
  $("stage-source").textContent = state.data?.fixture_mode ? "FIXTURE / NO API" : "STATIC DEMO";
}

function setProgress(value) {
  $("progress-fill").style.width = `${Math.max(0, Math.min(1, value)) * 100}%`;
}

function pauseAuto() {
  if (state.playing) state.elapsed += performance.now() - state.startedAt;
  state.playing = false;
  cancelAnimationFrame(state.raf);
  clearTimeout(state.autoTimer);
  state.raf = null;
  state.autoTimer = null;
  const btn = $("play-btn");
  btn.textContent = "播放";
  btn.setAttribute("aria-pressed", "false");
}

function tick(now) {
  if (!state.playing) return;
  const elapsed = state.elapsed + (now - state.startedAt);
  const p = Math.min(1, elapsed / ACT_MS);
  setProgress(p);
  if (p >= 1) {
    if (state.act < ACTS.length - 1) {
      state.elapsed = 0;
      state.startedAt = now;
      renderAct(state.act + 1, false);
      state.raf = requestAnimationFrame(tick);
    } else {
      pauseAuto();
      setProgress(1);
      $("play-btn").textContent = "重播";
    }
    return;
  }
  state.raf = requestAnimationFrame(tick);
}

function startAuto() {
  if (state.playing) return;
  if (state.act === ACTS.length - 1 && state.elapsed >= ACT_MS) {
    state.elapsed = 0;
    renderAct(0, false);
    state.elapsed = 0;
  }
  state.playing = true;
  state.startedAt = performance.now();
  const btn = $("play-btn");
  btn.textContent = "暂停";
  btn.setAttribute("aria-pressed", "true");
  state.raf = requestAnimationFrame(tick);
}

function toggleAuto() {
  if (state.playing) pauseAuto();
  else startAuto();
}

function go(delta) {
  pauseAuto();
  state.elapsed = 0;
  renderAct((state.act + delta + ACTS.length) % ACTS.length, true);
}

function selectAct(index) {
  pauseAuto();
  state.elapsed = 0;
  renderAct(index, true);
}

function setPresentation(on) {
  state.presenting = on;
  document.body.classList.toggle("is-present", on);
  $("present-btn").textContent = on ? "退出演示" : "演示模式";
  $("present-inline").textContent = on ? "退出" : "全屏";
  if (on) {
    $("stage").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
    startAuto();
  } else {
    pauseAuto();
  }
}

function openDemo() {
  $("stage").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
  selectAct(0);
  startAuto();
}

document.addEventListener("click", (event) => {
  const act = event.target.closest("[data-act]");
  if (act) selectAct(Number(act.dataset.act));
});
$("start-btn").addEventListener("click", openDemo);
$("play-btn").addEventListener("click", toggleAuto);
$("prev-btn").addEventListener("click", () => go(-1));
$("next-btn").addEventListener("click", () => go(1));
$("present-btn").addEventListener("click", () => setPresentation(!state.presenting));
$("present-inline").addEventListener("click", () => setPresentation(!state.presenting));

document.addEventListener("keydown", (event) => {
  if (event.target.closest("input, textarea, select")) return;
  if (event.key === "ArrowRight") { event.preventDefault(); go(1); }
  else if (event.key === "ArrowLeft") { event.preventDefault(); go(-1); }
  else if (event.key === " ") { if (event.target.closest("button,a")) return; event.preventDefault(); toggleAuto(); }
  else if (event.key === "Escape" && state.presenting) { event.preventDefault(); setPresentation(false); }
  else if (event.key.toLowerCase() === "p") { event.preventDefault(); setPresentation(!state.presenting); }
});

async function load() {
  try {
    const [demo, specs] = await Promise.all([
      fetch("data/demo.json", { cache: "no-store" }),
      fetch("data/specs.json", { cache: "no-store" })
    ]);
    if (!demo.ok) throw new Error("demo.json " + demo.status);
    state.data = await demo.json();
    state.specs = specs.ok ? await specs.json() : [];
    renderAct(0, false);
  } catch (error) {
    renderAct(0, false);
    $("stage-source").textContent = "FIXTURE MISSING";
    $("stage-title").textContent = "静态数据未载入";
    $("act-note").innerHTML = `<span class="note-kicker">STATIC DEMO</span><b class="note-title">从仓库根目录启动静态服务器</b><p class="note-body">为了在 GitHub Pages 或本地正确读取 data/demo.json，不要直接双击文件；运行 <code>python -m http.server</code> 或部署到 Pages。</p>`;
  }
}

load();
