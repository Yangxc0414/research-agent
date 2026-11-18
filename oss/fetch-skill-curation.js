// Curated skill snapshots: README + LICENSE + representative SKILL.md files.
// Uses GitHub Contents API because direct github.com git clone is blocked in this environment.
const fs = require("fs");
const path = require("path");
const https = require("https");

const ROOT = __dirname;
const REPOS = [
  {
    repo: "K-Dense-AI/scientific-agent-skills",
    dir: "Scientific-Agent-Skills-curated",
    starsNote: "公开报道 2026-08–10 约 33k–53k，仅作关注度",
    files: [
      "README.md", "LICENSE.md",
      "skills/literature-review/SKILL.md",
      "skills/scientific-writing/SKILL.md",
      "skills/statistical-analysis/SKILL.md",
      "skills/scanpy/SKILL.md",
      "skills/rdkit/SKILL.md"
    ]
  },
  {
    repo: "Imbad0202/academic-research-skills",
    dir: "Academic-Research-Skills-curated",
    starsNote: "2026-08 二手榜单约 42.1k，仅作关注度",
    files: [
      "README.md", "LICENSE",
      "academic-paper/SKILL.md",
      "academic-paper-reviewer/SKILL.md",
      "academic-pipeline/SKILL.md",
      "deep-research/SKILL.md"
    ]
  },
  {
    repo: "Orchestra-Research/AI-Research-SKILLs",
    dir: "AI-Research-SKILLs-curated",
    starsNote: "公开快照 2026-09–10 约 11.6k–14.5k，仅作关注度",
    files: [
      "README.md", "LICENSE",
      "0-autoresearch-skill/SKILL.md",
      "11-evaluation/lm-evaluation-harness/SKILL.md",
      "20-ml-paper-writing/ml-paper-writing/SKILL.md",
      "22-agent-native-research-artifact/rigor-reviewer/SKILL.md"
    ]
  }
];

function request(url, accept) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { "User-Agent": "Qoder", "Accept": accept } }, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode} ${url}\n${data.slice(0, 300)}`));
        } else {
          resolve(data);
        }
      });
    }).on("error", reject);
  });
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function encPath(p) { return p.split("/").map(encodeURIComponent).join("/"); }

(async () => {
  for (const spec of REPOS) {
    const target = path.join(ROOT, spec.dir);
    fs.mkdirSync(target, { recursive: true });
    const commitJson = JSON.parse(await request(`https://api.github.com/repos/${spec.repo}/commits/main`, "application/vnd.github+json"));
    const sha = commitJson.sha;
    await sleep(250);
    const saved = [];
    for (const rel of spec.files) {
      const raw = await request(`https://api.github.com/repos/${spec.repo}/contents/${encPath(rel)}?ref=${sha}`, "application/vnd.github.raw");
      const dest = path.join(target, rel);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, raw, "utf8");
      saved.push({ path: rel, bytes: Buffer.byteLength(raw) });
      await sleep(200);
    }
    const metadata = {
      repo: spec.repo,
      source_url: `https://github.com/${spec.repo}`,
      default_branch: "main",
      commit: sha,
      retrieved: "2026-10-23",
      stars_note: spec.starsNote,
      files: saved,
      note: "策展快照：仅 README、LICENSE 与代表性 SKILL.md；未下载脚本、参考文档、模板与完整技能目录，未运行、未复现。"
    };
    fs.writeFileSync(path.join(target, "metadata.json"), JSON.stringify(metadata, null, 2) + "\n", "utf8");
    const total = saved.reduce((a, f) => a + f.bytes, 0);
    const lines = [
      `# ${spec.repo} · 策展技能快照`,
      "",
      `> 来源：${metadata.source_url} · commit \`${sha}\` · 检索日期：2026-10-23`,
      `> 关注度：${spec.starsNote}`,
      `> 这不是完整仓库：只保留 README、LICENSE 与 ${saved.length - 2} 个代表性 SKILL.md，共 ${saved.length} 个文件、${(total / 1024).toFixed(1)} KB；未下载脚本、参考文档、模板与完整技能目录。`,
      "",
      "## 为什么选这些技能",
      "",
      "用于比较“技能如何组织、如何加载、如何声明输入输出/权限/证据要求”，而不是复现其效果。完整目录与安装方式见上游 README。",
      "",
      "## 文件",
      "",
      "| 文件 | 字节 |",
      "| --- | ---: |",
      ...saved.map((f) => `| ${f.path} | ${f.bytes} |`),
      "",
      "## 使用边界",
      "",
      "- 只读代码/文档，未运行任何技能；",
      "- 不引用其效果数字作为本项目结果；",
      "- 许可证以仓库 LICENSE 为准，二次分发前需再次核对。"
    ];
    fs.writeFileSync(path.join(target, "CURATION.md"), lines.join("\n") + "\n", "utf8");
    console.log(`${spec.repo} @ ${sha}: ${saved.length} files, ${(total / 1024).toFixed(1)} KB`);
  }
})().catch((err) => { console.error(err.message); process.exit(1); });
