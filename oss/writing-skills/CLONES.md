# `oss/writing-skills/` 写作 Skill 仓库清单

> 更新：2026-10-23 · 用途：为“中文期刊 / 英文学术 / 学位论文 / 基金”写作路由提供**完整**仓库底本。  
> 关系：[doc 21 §9.17](../../21-可落地系统设计与DeepSeek集成-证据闭合论文产出与Skill自进化.md) 定义 `WritingProfile` 与 skill bundle；本清单只记录仓库事实与使用限制。

---

## 1. 使用规则

- 本目录是**完整 git clone**（保留 `.git`、分支、历史）；不是 curated 摘录。
- 只用于本地阅读/适配，**不提交、不再分发**；根 `.gitignore` 已排除本目录，仅跟踪本文件。
- 复用任何 skill 前逐文件核对许可证与来源 commit；`Academic Research Skills` 是 **CC BY-NC 4.0**，只读对照、不进入产品交付。
- 不把 star 数、仓库自述效果当成质量或效果证据；不运行外部 skill 即宣称有效。
- **排除**以规避 AIGC 检测为目的的 humanizer / detector-rewriter 仓库（如 `academic-humanizer`、`AIGC-Detector-Rewriter`、`humanize-mba-text`）；我们的写作链路不做检测规避。

## 2. 总表

| 仓库 | 本地路径 | 类型 | Commit / Branch | Skill 数 | 许可 | 语言 / 定位 |
| --- | --- | --- | --- | --- | --- | --- |
| [zLanqing/codex-claude-academic-skills](https://github.com/zLanqing/codex-claude-academic-skills) | `zLanqing__codex-claude-academic-skills/` | `git-full` | `7ed6377` / `main` | 24 | MIT | 中文优先：论文写作/Word/PPT/科研工具 |
| [Master-cai/Research-Paper-Writing-Skills](https://github.com/Master-cai/Research-Paper-Writing-Skills) | `Master-cai__Research-Paper-Writing-Skills/` | `git-full` | `77e7c2c` / `main` | 1 | MIT | 英文 ML/CV/NLP 论文写作 |
| [SNL-UCSB/paper-writing-skill](https://github.com/SNL-UCSB/paper-writing-skill) | `SNL-UCSB__paper-writing-skill/` | `git-full` | `676f852` / `main` | 1 | MIT | 英文 systems/ML 修辞、压缩、red team |
| [lishix520/academic-paper-skills](https://github.com/lishix520/academic-paper-skills) | `lishix520__academic-paper-skills/` | `git-full` | `c325557` / `main` | 2 | MIT | 英文人文/交叉：strategist + composer |
| [LeonChaoX/qinyan-academic-skills](https://github.com/LeonChaoX/qinyan-academic-skills) | `LeonChaoX__qinyan-academic-skills/` | `git-full` | `df5a498` / `main` | 187 | MIT | 中英/基金/venue：scientific-writing、venue-templates、NSFC/NSSFC |
| [JingYangYuan/paper-write-4ss](https://github.com/JingYangYuan/paper-write-4ss) | `JingYangYuan__paper-write-4ss/` | `git-full` | `8f33bd4` / `main` | 1 | MIT | 中文社科写作：路由、章节、扫描、复杂度 |
| [Tianyuai/SCUT-Thesis-Writing-Skills](https://github.com/Tianyuai/SCUT-Thesis-Writing-Skills) | `Tianyuai__SCUT-Thesis-Writing-Skills/` | `git-full` | `f0f9ae8` / `main` | 1 | MIT | 中文学位论文：Word/格式/图表/盲审 |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | `Orchestra-Research__AI-Research-SKILLs/` | `git-full` | `773a529` / `main` | 98 | MIT | 英文科研/写作/评测：ml-paper-writing 等 |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | `Imbad0202__academic-research-skills/` | `git-full` | `5a1a5a6` / `main` | 5 | **CC BY-NC 4.0** | 英文论文流水线；只读对照 |

> Skill 数是仓库内 `SKILL.md` 的数量，包含嵌套参考/适配技能，不等于“独立原创 skill 数”。逐仓 `*.meta.json` 记录路径、commit、子模块/LFS 状态。

## 3. 各仓库能借什么

### 3.1 中文优先

- **zLanqing / research-writing-skill**：明确默认中文、先澄清 `journal/conference/thesis/course report + language + length + format`，并把 `原文/用户确认/推断/建议` 分开；适合作为中文写作的 base。
- **zLanqing / office-academic-skill**：中文 Word/PPT、DOCX 模板匹配、字体与版式检查；适合中文学位论文/报告交付。
- **JingYangYuan / paper-write-4ss**：中文社科，先做研究方法协议与发表范式路由，再章节写作；带 `writing_scanner.py` 与复杂度诊断。
- **Tianyuai / scut-thesis-writing**：以学校官方模板为最高依据，覆盖章节、公式、图表、DOCX 转换、格式审计、盲审；只适配华南理工，不能当通用校模板。

### 3.2 英文/国际

- **Master-cai / research-paper-writing**：ML/CV/NLP 的 section 结构、段落流、reviewer-facing presentation；来自 Peng Sida 公开笔记的整理（README 已注明 attribution）。
- **SNL-UCSB / paper-writing**：systems/ML 的五阶段写作、逐节 rhetorical moves、压缩、独立 red team；作者 voice 规则可自定义，不能直接当所有领域的默认 voice。
- **lishix520 / academic-paper-strategist + composer**：哲学/交叉学科，先平台分析、gap、outline，再写全稿；适合人文/交叉，不适合当作实验论文模板。
- **qinyan / scientific-writing + venue-templates**：IMRAD、APA/AMA/Vancouver、CONSORT/STROBE/PRISMA、Nature/Science/PLOS/IEEE/ACM/NeurIPS 等模板；英文 venue 适配的主力。
- **Orchestra-Research / ml-paper-writing**：英文 ML 写作与引文检查；与 Master-cai/SNL 组合，不单独当“全能写作器”。

### 3.3 基金/中文申报

- **qinyan / nsfc-proposal**：2026 NSFC 青年/优青/杰青，三模块、页限、AI 辅助声明；明确“AI 仅辅助检索/整理/润色，科学观点由申请人提供”。
- **qinyan / nssfc-proposal**：NSSFC 重点/一般/青年/西部，选题说明 300 字、活页匿名、学科差异。
- **qinyan / research-proposal**：英文/通用 proposal scaffold；与中文基金分开路由。

> 基金写作仍受 A3 边界：机器产草稿与检查，科学问题、创新点、预算与最终责任由申请人/负责人承担；不能自动生成“科学观点”冒充申请人。

### 3.4 Academic Research Skills：只读对照，不进产品

- 路径：`Imbad0202__academic-research-skills/`，commit `5a1a5a6`，5 个 `SKILL.md`：
  `academic-pipeline`、`academic-paper`、`academic-paper-reviewer`、`deep-research`、`sr-screener`。
- README/对外材料常描述“12-agent 论文流水线”；**以仓库实际 5 个 skill 为准**，不把宣传数字当结构事实。
- 许可证是 **CC BY-NC 4.0**：只读/对照，不打包进商业交付，不再分发。
- 可借：阶段划分、检查点、独立完整性检查、可恢复状态；不借：固定 10 阶段不可调整、Agent 数量堆叠、把模拟评审当同行评审。

## 4. 与 `WritingProfile` 的对应

| WritingProfile | 主 bundle |
| --- | --- |
| `zh_core_journal` | zLanqing `research-writing-skill` + JingYangYuan `paper-write-4ss` + 中文期刊模板 + `citation-audit` |
| `zh_thesis` | Tianyuai `scut-thesis-writing`（或学校对应模板）+ zLanqing `office-academic-skill` |
| `en_conference` | Master-cai `research-paper-writing` + SNL-UCSB `paper-writing` + AI-Research `ml-paper-writing` |
| `en_journal` | Master-cai + SNL-UCSB + qinyan `scientific-writing`/`venue-templates` |
| `grant_zh` | qinyan `nsfc-proposal` / `nssfc-proposal` / `research-proposal` |
| `humanities` | lishix520 strategist/composer；中文社科用 JingYangYuan |

## 5. 复核

```bash
# 逐仓确认完整历史
for d in oss/writing-skills/*/; do
  [ -d "$d/.git" ] && git -C "$d" rev-parse --short HEAD && git -C "$d" rev-parse --is-shallow-repository
done

# 查看 manifest / 元数据
cat oss/writing-skills/manifest.json
```

> 未完成/待核对的仓库保持“进行中/待核对”，不写成完整 clone；所有外部效果数字不进入我们的结论。
