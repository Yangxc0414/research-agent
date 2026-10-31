import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const site = path.join(root, "site");
const demoSource = path.join(root, "demo", "index.html");
const demoDir = path.join(site, "demo");

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

function copyInnovationData() {
  const sourceDir = path.join(root, "research_agent", "web", "data");
  const targetDir = path.join(site, "innovation", "data");
  if (!fs.existsSync(sourceDir)) {
    console.warn("skip innovation data: research_agent/web/data not found");
    return [];
  }
  ensureDir(targetDir);
  const names = [
    "demo.json",
    "specs.json",
    "figure.svg",
    "figure.scene.json",
    "figure.manifest.json",
    "paper.json",
    "grant.json"
  ];
  const copied = [];
  for (const name of names) {
    const source = path.join(sourceDir, name);
    if (!fs.existsSync(source)) continue;
    fs.copyFileSync(source, path.join(targetDir, name));
    copied.push(name);
  }
  return copied;
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
const innovationData = copyInnovationData();
const jsonFiles = validateJsonDir(path.join(site, "data"));

const buildInfo = {
  built_at: new Date().toISOString(),
  demo_sha256_16: demoHash,
  docs: [],
  data_files: jsonFiles,
  innovation_data: innovationData
};
fs.writeFileSync(path.join(site, "data", "build.json"), JSON.stringify(buildInfo, null, 2) + "\n");

console.log("site build ok");
console.log("  demo:", "site/demo/index.html", "sha256:" + demoHash);
console.log("  data:", jsonFiles.length ? jsonFiles.join(", ") : "(none)");
console.log("  innovation data:", innovationData.length ? innovationData.join(", ") : "(none)");
console.log("  preview: npx serve site");
