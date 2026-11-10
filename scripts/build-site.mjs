import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const site = path.join(root, "site");
const demoSource = path.join(root, "demo", "index.html");
const demoDir = path.join(site, "demo");
const docsDir = path.join(site, "docs");

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function copyDemo() {
  if (!fs.existsSync(demoSource)) {
    throw new Error("demo/index.html not found");
  }
  ensureDir(demoDir);
  fs.copyFileSync(demoSource, path.join(demoDir, "index.html"));
  const hash = crypto.createHash("sha256").update(fs.readFileSync(demoSource)).digest("hex").slice(0, 16);
  return hash;
}

function copyDocs() {
  ensureDir(docsDir);
  const docs = [
    ["README.md", "README.md"],
    ["16-科研Skill生态调研与动态流程编排.md", "16-科研Skill生态调研.md"],
    ["17-基于Skill契约的上层微服务架构.md", "17-上层微服务架构.md"],
    ["18-GitHub Pages部署与多智能体Skill设计.md", "18-GitHub Pages部署与多智能体Skill设计.md"]
  ];
  const copied = [];
  for (const [source, target] of docs) {
    const sourcePath = path.join(root, source);
    if (!fs.existsSync(sourcePath)) {
      console.warn("skip missing doc:", source);
      continue;
    }
    fs.copyFileSync(sourcePath, path.join(docsDir, target));
    copied.push(target);
  }
  return copied;
}

function copyInnovationData() {
  const sourceDir = path.join(root, "research_agent", "web", "data");
  const targetDir = path.join(site, "innovation", "data");
  ensureDir(targetDir);
  const copied = [];
  if (fs.existsSync(sourceDir)) {
    const names = [
      "demo.json",
      "figure.svg",
      "figure.scene.json",
      "figure.manifest.json",
      "paper.json",
      "grant.json"
    ];
    for (const name of names) {
      const source = path.join(sourceDir, name);
      if (!fs.existsSync(source)) continue;
      fs.copyFileSync(source, path.join(targetDir, name));
      copied.push(name);
    }
  } else {
    console.warn("skip innovation runtime data: research_agent/web/data not found");
  }
  // Single source of truth: the innovation demo and the app workbench both read the
  // workspace registry exported from modules/*/SPEC.md, so their module versions and
  // statuses can never drift apart.
  const registryPath = path.join(root, "apps", "web", "public", "agent-registry.json");
  if (fs.existsSync(registryPath)) {
    const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
    fs.writeFileSync(path.join(targetDir, "specs.json"), JSON.stringify(registry.agents || [], null, 2) + "\n");
    copied.push("specs.json");
  }
  return copied;
}

function copyStats() {
  // The showcase must not hard-code a test count that rots. Pull the recorded verdict (which
  // carries the code fingerprint it covers) so the page can show a number with a provenance, or
  // honestly show "—" when no verdict exists.
  const source = path.join(root, "runtime_data", "test-verdict.json");
  const targetDir = path.join(site, "innovation", "data");
  if (!fs.existsSync(source)) return null;
  try {
    const verdict = JSON.parse(fs.readFileSync(source, "utf8"));
    ensureDir(targetDir);
    const stats = {
      tests_run: verdict.tests_run ?? null,
      ok: verdict.ok ?? false,
      source_fingerprint: verdict.source_fingerprint ?? "",
      finished_at: verdict.finished_at ?? "",
    };
    fs.writeFileSync(path.join(targetDir, "stats.json"), JSON.stringify(stats, null, 2) + "\n");
    return stats;
  } catch {
    return null;
  }
}

function validateJsonDir(dir) {
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter((name) => name.endsWith(".json"));
  for (const file of files) {
    const full = path.join(dir, file);
    try {
      JSON.parse(fs.readFileSync(full, "utf8"));
    } catch (error) {
      throw new Error("invalid JSON: " + full + " — " + error.message);
    }
  }
  return files;
}

const demoHash = copyDemo();
const docs = copyDocs();
const innovationData = copyInnovationData();
const stats = copyStats();
const jsonFiles = validateJsonDir(path.join(site, "data"));

const buildInfo = {
  built_at: new Date().toISOString(),
  demo_sha256_16: demoHash,
  docs,
  data_files: jsonFiles,
  innovation_data: innovationData,
  stats
};
fs.writeFileSync(path.join(site, "data", "build.json"), JSON.stringify(buildInfo, null, 2) + "\n");

console.log("site build ok");
console.log("  demo:", "site/demo/index.html", "sha256:" + demoHash);
console.log("  docs:", docs.length ? docs.join(", ") : "(none)");
console.log("  data:", jsonFiles.length ? jsonFiles.join(", ") : "(none)");
console.log("  innovation data:", innovationData.length ? innovationData.join(", ") : "(none)");
console.log("  preview: npx serve site");
