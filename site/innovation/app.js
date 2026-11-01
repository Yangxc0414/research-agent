const ACT_MS = 6200;
const MOTION_OFF = /[?&]motion=off\b/.test(location.search);
const REDUCED = MOTION_OFF || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
document.documentElement.classList.add(REDUCED ? "still" : "motion");
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
    key: "evidence", name: "证据", sub: "SPAN · 资格判定", title: "证据不是聊天记录。",
    noteTitle: "摘要不是证据",
    noteBody: "检索、全文、句级 span、覆盖回执分开记录；没有全文就不能生成 span，更不能创建 Claim。这是对每句结论的第一问：这句话有资格写吗。",
    noteFact: "0", noteFactLabel: "claims from S1", tags: ["QueryPlan", "Span", "CoverageReceipt"]
  },
  {
    key: "paper", name: "稿件", sub: "SLOT · 完成判定", title: "写作可以并行，结果不能抢跑。",
    noteTitle: "结果槽保持 pending",
    noteBody: "论文和基金只产骨架。没有 EA/Claim，结果槽不填；G5 导出保持 blocked，示意图不能绑成结果图。签署之前，运行不承认任何结果。",
    noteFact: "5", noteFactLabel: "PENDING SLOTS", tags: ["PaperContract", "G5 blocked", "人签"]
  },
  {
    key: "figure", name: "图", sub: "SVG · 源头可查", title: "图也要有 provenance。",
    noteTitle: "先审计，再交付",
    noteBody: "AstraDraw 负责 scene→SVG；我们审计 XML、ID、文本、外部引用和 aria，并把哈希写进 manifest。结果图与示意图强制分离。",
    noteFact: "PASS", noteFactLabel: "SVG AUDIT", tags: ["scene hash", "svg hash", "no external"]
  },
  {
    key: "spec", name: "契约", sub: "SPEC · 唯一事实源", title: "先写契约，再写代码。",
    noteTitle: "最小的可演进单元",
    noteBody: "28 个子智能体都有 SPEC.md。改行为先改契约，再用 CLI 做最小更新；绕过 claim / export 的路径有专门的拒绝测试。",
    noteFact: "28", noteFactLabel: "SPEC · 119 TEST FILES", tags: ["SPEC = single source", "拒绝测试", "changelog"]
  },
  {
    key: "trace", name: "运行", sub: "TRACE · 全程留痕", title: "智能体的每一步，都留痕。",
    noteTitle: "拦截记录，不是错误堆栈",
    noteBody: "PIPE-20261031T163234Z 实测快照的阶段重放：智能体每一步做什么、报什么、被拦在哪。它说“做不了”的时候，留下的是可复核的拦截记录，而不是一条错误日志。",
    noteFact: "2", noteFactLabel: "REAL INTERCEPTS", tags: ["stage replay", "全程留痕", "needs_human 终态"]
  },
  {
    key: "boundary", name: "边界", sub: "CLAIM · 说“不”是设计", title: "边界不是免责，是设计。",
    noteTitle: "把“不”写进代码",
    noteBody: "六幕本体是 fixture；真实接线在 LIVE WIRING：统计门槛与设计审计两次拦下模型草稿，结果槽锁定等待作者签署。说“不”的记录，就是这套系统的创新点记录。",
    noteFact: "0", noteFactLabel: "SIGN ENDPOINTS IN MCP", tags: ["fixture acts", "两次真实拦截", "四个判定"]
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
  return `<div class="act-head"><p class="eyebrow">ACT 04 / SPEC · 唯一事实源</p><h2>${esc(ACTS[3].title)}</h2><p>六模块同构：输入、输出、门禁、不变量、实现边界都写在 Markdown 里；代码读取版本，CLI 只改指定字段。</p></div>
    <div class="spec-grid">${ids.map((id) => `<article class="spec-card" data-kind="${moduleMeta(id).kind}"><b>${esc(moduleMeta(id).label)}</b><small>${esc(specOf(id)?.stage || "")} · v${esc(specOf(id)?.version || state.data.spec_versions?.[id] || "—")}</small><em>${esc(statusOf(id))}</em></article>`).join("")}</div>
    <div class="spec-console"><span class="prompt">$</span> python -m research_agent spec update figure \\
  --version 0.1.1 --status pilot \\
  --changelog "最小改进：增加 SVG 审计"
<span class="prompt">→</span> 单模块落盘：正文保留 · changelog 追加 · 不越界</div>
    <div class="spec-points"><span>SPEC = single source</span><span>最小的 diff</span><span>version / changelog</span><span>tests first</span></div>`;
}

function evidenceAct() {
  const lit = state.data.modules.literature || {};
  const coverage = lit.coverage || {};
  const spans = (lit.spans || []).slice(0, 3);
  return `<div class="act-head"><p class="eyebrow">ACT 01 / EVIDENCE · 资格判定</p><h2>${esc(ACTS[0].title)}</h2><p>检索计划、来源命中、全文读取、句级 span 和覆盖缺口分开记录。摘要-only 只能作为线索，不能成为证据。</p></div>
    <div class="metric-row">
      <div class="metric"><b data-count="${coverage.sources_found ?? 0}">0</b><span>SOURCES FOUND</span><em>${coverage.sources_read ?? 0} full texts read</em></div>
      <div class="metric"><b data-count="${coverage.spans_extracted ?? 0}">0</b><span>SPANS EXTRACTED</span><em>sentence-level anchors</em></div>
      <div class="metric"><b data-count="${(coverage.gaps || []).length}">0</b><span>COVERAGE GAPS</span><em>reported, not hidden</em></div>
    </div>
    <div class="flow-diagram" data-flow>
      <span class="flow-node"><b>QueryPlan</b><small>检索计划</small></span>
      <span class="flow-node"><b>SourceHit</b><small>来源线索</small></span>
      <span class="flow-node"><b>全文</b><small>full text</small></span>
      <span class="flow-node"><b>Span</b><small>句级定位</small></span>
      <span class="flow-node"><b>CoverageReceipt</b><small>覆盖回执</small></span>
      <span class="flow-node is-gap"><b>Gap</b><small>覆盖缺口</small></span>
    </div>
    <p class="fig-caption">图 1 · 证据链 artifact：QueryPlan → SourceHit → 全文 → Span → CoverageReceipt / Gap；摘要-only 在第二步就被阻断。</p>
    <div class="span-stack">${spans.map((span) => `<div class="span-item"><code>${esc(span.span_id)} · ${esc(span.section)}</code>${esc(span.text)}</div>`).join("") || `<div class="span-item">没有 span。先补全文。</div>`}</div>
    <div class="gap-line">${(coverage.gaps || []).map((gap) => `<span class="gap-chip">${esc(gap.code)}</span>`).join("") || `<span class="gap-chip">no gap reported</span>`}</div>`;
}

function figureAct() {
  const figure = state.data.modules.figure || {};
  const audit = figure.audit || {};
  const checks = Object.entries(audit.checks || {}).filter(([key, value]) => typeof value === "boolean");
  return `<div class="act-head"><p class="eyebrow">ACT 03 / SVG · 源头可查</p><h2>${esc(ACTS[2].title)}</h2><p>scene 由我们的 FigureAgent 生成，AstraDraw 渲染成 SVG；交付前必须通过可访问性、安全与文本检查。</p></div>
    <div class="figure-showcase"><img src="data/figure.svg" alt="研究运行时模块关系示意图；示意图，不是实验结果" /></div>
    <div class="audit-list">${checks.map(([key, value]) => `<div class="audit-row"><span class="audit-tick">${value ? "✓" : "×"}</span><span>${esc(CHECK_LABELS[key] || key)}</span></div>`).join("")}</div>
    <div class="hash-line"><span>SCENE ${esc((figure.manifest?.scene_sha256 || "").slice(0, 18))}…</span><span>SVG ${esc((figure.manifest?.svg_sha256 || "").slice(0, 18))}…</span><span>SCHEMATIC</span></div>
    <p class="fig-caption">图 2 · AstraDraw scene → SVG：审计通过后 manifest 同时记录 scene 与 svg 的 SHA-256。</p>`;
}

function paperAct() {
  const paper = state.data.modules.paper || {};
  const grant = state.data.modules.grant;
  const g5 = (state.data.gates || []).find((gate) => gate.gate === "G5") || {};
  return `<div class="act-head"><p class="eyebrow">ACT 02 / SLOTS + GATES · 完成判定</p><h2>${esc(ACTS[1].title)}</h2><p>论文与基金共享同一套 Evidence 约束：方法/结构可以先写，结果槽必须等 EA；示意图不能被冒充成结果图。</p></div>
    <div class="flow-diagram" data-flow>
      <span class="flow-node ok"><b>EA</b><small>封存后</small></span>
      <span class="flow-node is-gate"><b>Claim</b><small>作者签署</small></span>
      <span class="flow-node is-gate"><b>Closure</b><small>全部通过</small></span>
      <span class="flow-node is-blocked"><b>G5 Export</b><small>此前 blocked</small></span>
    </div>
    <p class="fig-caption">图 3 · 结果路径：EA 封存 → 作者签署 Claim → Closure 全过 → G5 才放行导出。</p>
    <div class="slot-grid">${(paper.slots || []).map((slot) => `<div class="slot-card"><b>${esc(slot.slot_id)}</b><span>${esc(slot.section)} · ${esc(slot.required_evidence)}</span><span class="slot-pill">${esc(slot.status)}</span></div>`).join("")}</div>
    <div class="track-grid">
      <div class="track-card"><span class="mono">PAPER TRACK</span><h3>${esc(paper.profile?.venue_type || "论文契约")}</h3><p>${esc(paper.profile?.citation_style || "GB/T 7714")} · ${(paper.sections || []).length} sections · 0 claims</p></div>
      <div class="track-card"><span class="mono">GRANT TRACK</span><h3>${grant ? esc(grant.scheme.toUpperCase()) : "未生成"}</h3><p>${grant ? `${(grant.modules || []).length} modules · ${(grant.compliance || []).length} compliance checks` : "用 --grant nsfc 生成基金骨架"}</p></div>
    </div>
    <div class="gate-banner"><span>G5 EXPORT · ${esc(g5.status || "blocked")}</span><b>${esc(g5.reason || "no EA/Closure")}</b></div>`;
}

function boundaryAct() {
  return `<div class="act-head"><p class="eyebrow">ACT 06 / BOUNDARY</p><h2>${esc(ACTS[4].title)}</h2><p>这一页不把 fixture 说成实验，也不把“架构更清楚”说成“科研效果更好”。能证明的和不能证明的分开写。</p></div>
    <div class="boundary-grid">
      <div class="boundary-card"><b>不是通用 AI 科学家</b><p>机器负责检索、草稿、图、核验；科学决策、实验安全、署名与责任在人。</p></div>
      <div class="boundary-card"><b>不是效果论文</b><p>当前没有真实检索、run/EA、用户研究；不引用任何外部效果数字。</p></div>
      <div class="boundary-card"><b>可检验的工程差异</b><p>28 份 SPEC、119 个测试文件、32 个数据契约、SVG audit、结果槽阻断；这些都能在代码里找到。</p></div>
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

/* ---- ACT 05 数据：实测快照的阶段重放（时间轴为相对时刻） ---- */
const TRACE = [
  { t: "00:00", stage: "plan", text: "生成检索计划：13 条中英双语查询，覆盖综述 / 方法 / 评测 / 局限 / 最新进展", status: "ok", sub: "S1 planner · agnes-2.5-flash · 6.5s · 471 tok · 审计只记元数据" },
  { t: "00:07", stage: "retrieve", text: "CC-BY 冻结语料 probe → 3 个来源命中，2 篇全文送达", status: "ok" },
  { t: "00:09", stage: "span", text: "全文句级定位 → 5 个 spans；摘要-only 来源不产 span", status: "ok", sub: "上报 3 条覆盖缺口——缺口是产出，不是失误" },
  { t: "00:12", stage: "synthesis", text: "主题 × 来源矩阵：一致 4 · 张力 1 · 未使用 1", status: "ok" },
  { t: "00:15", stage: "idea", text: "3 条候选，各带假设与可否证条件 → G1 交回人工", status: "warn", sub: "「……因果推断均超出了 Fixture 数据的有效范围」——模型自己指出数据边界（IDEA-03）" },
  { t: "00:31", stage: "design", text: "S4 草案提交 design-audit → BLOCKER", status: "block", sub: "缺 stopping budget 字段：退回补齐，而不是替模型猜一个" },
  { t: "00:44", stage: "design", text: "补齐预算后重审 → ready_for_g2", status: "ok" },
  { t: "00:52", stage: "gate", text: "G2：人工确认设计、数据与统计口径", status: "hold" },
  { t: "01:03", stage: "study", text: "模型起草沿用 3 seeds → 统计门槛拒绝", status: "block", sub: "配对种子 <4 不写任何文件；改为 4 配对种子重新执行" },
  { t: "01:10", stage: "study", text: "iris · 4 配对种子真实执行", status: "ok", sub: "CI95 [-0.41, 0.51] 跨零 → 如实判「不可判定」；power note：同效应 80% 功效需 263 种子" },
  { t: "01:38", stage: "figure", text: "示意图 scene → SVG · 审计 9 项全过", status: "ok", sub: "scene / svg 双 SHA-256 写进 manifest；结果图与示意图分离" },
  { t: "01:52", stage: "paper", text: "方法与结构章节起草 · 结果槽 5 × pending", status: "hold", sub: "模型可以写骨架；结果句没有 EA 资格" },
  { t: "02:07", stage: "terminal", text: "needs_human：结果锁定，等待作者签署 claim", status: "hold", sub: "门禁没有让步——export 在 closure + 签名之前始终 blocked" }
];
const TRACE_MARK = { ok: "✓", warn: "⚠", block: "⛔", hold: "⏸" };

function traceAct() {
  return `<div class="act-head"><p class="eyebrow">ACT 05 / RUN TRACE · 全程留痕</p><h2>${esc(ACTS[4].title)}</h2><p>把 PIPE-20261031T163234Z 实测快照按阶段重放：智能体每一步做什么、报什么、被拦在哪。时间为相对时刻；拦截与等待都是产出。</p></div>
    <div class="trace-list">${TRACE.map((line, i) => `<div class="trace-line is-${line.status}" style="--td:${Math.min(i * 110, 1400)}ms"><span class="trace-t">${esc(line.t)}</span><span class="trace-stage">${esc(line.stage)}</span><span class="trace-main"><b>${esc(line.text)}</b>${line.sub ? `<small>${esc(line.sub)}</small>` : ""}</span><span class="trace-mark" aria-hidden="true">${TRACE_MARK[line.status]}</span></div>`).join("")}</div>
    <div class="trace-legend"><span class="is-ok">✓ 完成</span><span class="is-warn">⚠ 需人复核</span><span class="is-block">⛔ 拦截</span><span class="is-hold">⏸ 等待 / 暂停</span></div>`;
}

const RENDERERS = [evidenceAct, paperAct, figureAct, specAct, traceAct, boundaryAct];

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

/* ---- flow diagrams：框 + SVG 连线 + 箭头（自动换行/resize 重算） ---- */
function drawFlows(root) {
  root.querySelectorAll("[data-flow]").forEach((container) => {
    const nodes = Array.from(container.querySelectorAll(":scope > .flow-node"));
    const w = container.scrollWidth || container.offsetWidth;
    const h = container.scrollHeight || container.offsetHeight;
    if (nodes.length < 2 || !w || !h) return;
    if (!container.dataset.flowId) {
      container.dataset.flowId = "fv" + Math.random().toString(36).slice(2, 8);
    }
    const key = container.dataset.flowId;
    let svg = container.querySelector(":scope > svg.flow-svg");
    if (!svg) {
      svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "flow-svg");
      container.insertBefore(svg, container.firstChild);
    }
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.setAttribute("width", String(w));
    svg.setAttribute("height", String(h));
    const cRect = container.getBoundingClientRect();
    const pts = nodes.map((node) => {
      const r = node.getBoundingClientRect();
      return {
        left: r.left - cRect.left, right: r.right - cRect.left,
        top: r.top - cRect.top, bottom: r.bottom - cRect.top,
        cx: r.left - cRect.left + r.width / 2, cy: r.top - cRect.top + r.height / 2
      };
    });
    let body = "";
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1];
      let pathD;
      if (b.left >= a.right - 8) {
        const mx = (a.right + 2 + b.left - 4) / 2;
        pathD = `M ${a.right + 2} ${a.cy} C ${mx} ${a.cy}, ${mx} ${b.cy}, ${b.left - 4} ${b.cy}`;
      } else if (b.top >= a.bottom - 8) {
        const my = (a.bottom + 2 + b.top - 4) / 2;
        pathD = `M ${a.cx} ${a.bottom + 2} C ${a.cx} ${my}, ${b.cx} ${my}, ${b.cx} ${b.top - 4}`;
      } else {
        pathD = `M ${a.cx} ${a.cy} L ${b.cx} ${b.cy}`;
      }
      const gated = /is-gate|is-gap|is-blocked/.test(nodes[i + 1].className);
      body += `<g class="flow-link-g" style="animation-delay:${Math.min(i * 90, 900)}ms"><path class="flow-link${gated ? " is-to-gate" : ""}" marker-end="url(#arrow-${key})" d="${pathD}"/></g>`;
    }
    svg.innerHTML = `<defs><marker id="arrow-${key}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 z" fill="#8a94b8"/></marker></defs>${body}`;
  });
}
let flowRaf = null;
function scheduleFlows() {
  if (flowRaf) return;
  flowRaf = requestAnimationFrame(() => { flowRaf = null; drawFlows(document); });
}
window.addEventListener("resize", scheduleFlows);
window.addEventListener("load", scheduleFlows);

function renderAct(index, animate = true) {
  state.act = Math.max(0, Math.min(ACTS.length - 1, index));
  const act = ACTS[state.act];
  $("stage-act-label").textContent = `0${state.act + 1} / ${String(ACTS.length).padStart(2, "0")}`;
  $("stage-title").textContent = act.title;
  const canvas = $("act-canvas");
  if (!state.data) {
    canvas.innerHTML = `<div class="act-head"><p class="eyebrow">FIXTURE NOT LOADED</p><h2>先运行 fixture pipeline。</h2><p>从项目根目录运行 <code>python -m research_agent pipeline run ...</code>，再启动静态服务器。当前页面不会调用 API。</p></div>`;
  } else {
    canvas.innerHTML = RENDERERS[state.act]();
    drawFlows(canvas);
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

/* ---- 滚动入场 + 分节导航高亮（reduced-motion 或 ?motion=off 时全部停用） ---- */
function setupReveals() {
  if (REDUCED || !("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      io.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
}

function setupNavSpy() {
  const topbar = document.querySelector(".topbar");
  const hero = document.querySelector(".hero");
  if (!topbar || !hero) return;
  if (!("IntersectionObserver" in window)) { topbar.classList.add("is-scrolled"); return; }
  new IntersectionObserver((entries) => {
    topbar.classList.toggle("is-scrolled", !entries[entries.length - 1].isIntersecting);
  }, { threshold: 0.06 }).observe(hero);
  const links = Array.from(document.querySelectorAll(".nav-menu a[data-section]"));
  if (!links.length) return;
  const spy = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((link) => link.classList.toggle("is-active", link.dataset.section === entry.target.id));
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  ["judgments", "demo", "wiring", "proof", "cite"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) spy.observe(el);
  });
}

function setupCopyBib() {
  const btn = $("copy-bib");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const text = $("bib-text").textContent;
    let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; }
    catch (error) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
      ta.remove();
    }
    if (!ok) return;
    btn.classList.add("is-done");
    btn.querySelector("span").textContent = "已复制";
    setTimeout(() => {
      btn.classList.remove("is-done");
      btn.querySelector("span").textContent = "复制";
    }, 1800);
  });
}

document.addEventListener("click", (event) => {
  const act = event.target.closest("[data-act]");
  if (act) selectAct(Number(act.dataset.act));
});
document.querySelectorAll(".orbit-node[data-act]").forEach((node) => {
  node.addEventListener("click", () => {
    $("stage").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
    selectAct(Number(node.dataset.act));
  });
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
scheduleFlows();
setupReveals();
setupNavSpy();
setupCopyBib();
