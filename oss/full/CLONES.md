# `oss/full/` 完整仓库清单

> 更新：2026-10-23 21:47 · 维护方式：每次 clone/下载后更新本表  
> 目的：给“自改进机制对照”和工程参考提供**可审计**的仓库副本；不是产品依赖，不随站点发布。  
> 相关：[`../README.md`](../README.md) · [doc 20](../../20-开源科研Agent框架调研-浙大SciToolAgent与主流技术栈.md) · [doc 23](../../23-开源自改进机制对照-从A-Evolve-RSI-Anything到我们的Lease-Gated-Runtime.md)

---

## 0. 三种“下载完成”不是一回事

| 类型 | 有什么 | 没有什么 | 本文标记 |
| --- | --- | --- | --- |
| **完整 git clone** | 完整提交历史、branch、tag、`.git`；递归子模块；LFS 对象（若有） | 无 | `git-full` |
| **完整工作树快照** | 上游某一 commit 的全部工作树文件；可用 README/文件哈希与上游核对 | `.git` 历史、子模块内容、LFS 实体（ZIP 通常只含指针） | `tree-snapshot` |
| **部分 clone** | 只下载到一部分对象/文件，不能代表仓库完整 | 完整性 | `partial` |

> 规则：**没有 `.git` 就不写“完整 clone”**；没有运行就不写“已验证可复现”；没有核对 commit 就不写“对应某个版本”。网络受限时宁可用 `tree-snapshot` 并标明，不用浅拷贝冒充完整历史。

## 1. 总表

| 上游仓库 | 本地路径 | 类型 | Commit / Branch | 体积 | 许可证（以 LICENSE 为准） | 子模块 / LFS | 主要用途 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [HICAI-ZJU/SciToolAgent](https://github.com/HICAI-ZJU/SciToolAgent) | `HICAI-ZJU__SciToolAgent/` | `git-full` | `ac1cf19` / `main` | 70 MB | MIT | 0 / 0 | 工具知识图谱、FastAPI、工具编排 | ✅ 已核对 |
| [ResearAI/DeepScientist](https://github.com/ResearAI/DeepScientist) | `ResearAI__DeepScientist/` | `git-full` | `b366244` / `main` | 204 MB（`.git` 76 MB） | Apache-2.0 | 0 / 0 | 逐轮 prompt、skills、memory/artifact、guidance | ✅ 已核对 |
| [zhu-minjun/Researcher](https://github.com/zhu-minjun/Researcher)（CycleResearcher） | `zhu-minjun__Researcher/`（`git-full`）；`_zip/zhu-minjun__Researcher/`（回退快照） | `git-full` | `8c1b253` / `main` | 27 MB | **CycleResearcher License**（研究专用，非 OSI） | 0 / 0 | 模型级 RL 对照 | ✅ 已核对；**不复用/不再分发** |
| [SakanaAI/AI-Scientist-v3](https://github.com/SakanaAI/AI-Scientist-v3) | `SakanaAI__AI-Scientist-v3/`（`git-full`）；`_zip/SakanaAI__AI-Scientist-v3/`（回退快照） | `git-full` | `df83138` / `main` | 20 MB | Apache-2.0 | 0 / 0 | Docker/run/rubric 的单轮自验证 | ✅ 已核对 |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | `_zip/assafelovic__gpt-researcher/` | `tree-snapshot` | `3582a68` / `main` | 28 MB（ZIP 14.2 MB） | Apache-2.0 | 0 / 0 | 前后端分离、报告/引用 | ✅ 完整工作树；无 `.git` |
| [HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) | `_partial/HKUDS__AI-Researcher/`（中断） | `partial` | `f9a6f84` / `main` | 26 MB（仅 `.git` 对象） | 仓库页未声明 | 未核 | idea→文献→实现→论文 | ⚠️ 工作树 901 MB（大量 examples GIF/数据集），归档下到 263 MB 后停止 |
| [InternScience/InternAgent](https://github.com/InternScience/InternAgent) | `_zip/InternScience__InternAgent/` | `tree-snapshot` | `fa8c3ee` / `main` | 41 MB（ZIP 18 MB） | Apache-2.0 | **子模块未拉取**：`sci_tasks` → `ResearchClawBench` @ `9b5288e`（上游 1.1 GB）；无 LFS | 长时程任务/MCTS | ⚠️ 主树完整且 README 哈希匹配；子模块待补 |
| [SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | `_zip/SamuelSchmidgall__AgentLaboratory/` | `tree-snapshot` | `d9017d9` / `main` | 1.7 MB（ZIP 1.3 MB） | MIT | 0 / 0 | 多角色端到端 | ✅ 完整工作树；README 哈希匹配；无 `.git` |
| [snap-stanford/Biomni](https://github.com/snap-stanford/Biomni) | `_zip/snap-stanford__Biomni/` | `tree-snapshot` | `400c1f3` / `main` | 3.9 MB（ZIP 1.0 MB） | Apache-2.0 | 0 / 0 | 生物医学工具/数据 | ✅ 完整工作树；README 哈希匹配；无 `.git` |
| [aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw) | `_zip/aiming-lab__AutoResearchClaw/`（旧快照仍在 `../AutoResearchClaw-main/`） | `tree-snapshot` | `be4ba47` / `main` | 50.1 MB（ZIP 44.3 MB） | MIT | 0 / 0 | A-Evolve、23 阶段、HITL | ✅ 完整工作树；无 `.git` |
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | `_zip/wanshuiyin__Auto-claude-code-research-in-sleep/`（旧快照仍在 `../Auto-claude-code-research-in-sleep-main/`） | `tree-snapshot` | `23745b6` / `main` | 37.1 MB（ZIP 25.3 MB） | MIT | 0 / 0 | ARIS 对抗评审/状态恢复 | ✅ 完整工作树；无 `.git` |
| [EvoMap/AutoResearch](https://github.com/EvoMap/AutoResearch) | `_zip/EvoMap__AutoResearch/`（旧快照仍在 `../AutoResearch-main/`） | `tree-snapshot` | `21f5912` / `main` | 1.9 MB（ZIP 0.9 MB） | Apache-2.0 | 0 / 0 | Coordinator/Ralph loop/memory | ✅ 完整工作树；无 `.git` |
| [Gen-Verse/RSI-Anything](https://github.com/Gen-Verse/RSI-Anything) | `_zip/Gen-Verse__RSI-Anything/`（旧快照仍在 `../RSI-Anything-main/`） | `tree-snapshot` | `8ba44cd` / `main` | 17.4 MB（ZIP 11.1 MB） | Apache-2.0 | 0 / 0 | retained pair、incumbent guard | ✅ 完整工作树；无 `.git` |
| [OpenRSI-Foundation/OpenRSI-Index](https://github.com/OpenRSI-Foundation/OpenRSI-Index) | `_zip/OpenRSI-Foundation__OpenRSI-Index/`（旧快照仍在 `../OpenRSI-Index-main/`） | `tree-snapshot` | `12e10fd` / `main` | 131.5 MB（ZIP 82.3 MB） | Apache-2.0 | 0 / 0 | Work/Judge/私有测试 | ✅ 完整工作树；无 `.git` |
| [DAIR-AutoResearch/AutoSci](https://github.com/DAIR-AutoResearch/AutoSci) | `_zip/DAIR-AutoResearch__AutoSci/`（旧快照仍在 `../AutoSci-main/`） | `tree-snapshot` | `f676a03` / `main` | 15.4 MB（ZIP 12.1 MB） | MIT | 0 / 0 | wiki 中心记忆/全生命周期 | ✅ 完整工作树；无 `.git` |

> “体积”是本地磁盘占用，不等于仓库对象大小；`git-full` 包含 `.git`，通常比工作树大。  
> “旧快照”在 `oss/` 根下，来自更早一轮下载，commit 见 [`../metadata.json`](../metadata.json)；本表只把它们当参考，不冒充 `oss/full/` 的完整 clone。

## 2. 已完成的逐项核对

### 2.1 SciToolAgent（`git-full`）

- 路径：`oss/full/HICAI-ZJU__SciToolAgent`
- HEAD：`ac1cf19fcef84e69f149db6da424afe4e9b2f11f`，branch `main`，提交时间 2025-08-26
- 远程：`https://github.com/HICAI-ZJU/SciToolAgent.git`
- 许可证：MIT（根 `LICENSE`）
- 子模块：`git submodule status` 为空；LFS：`git lfs ls-files` 为空
- 用途：只读对照其工具注册/安全属性/Planner-Executor-Summarizer；**不把请求体传 API key 的做法带进我们的设计**
- 未运行：仓库的 500+ 工具与 API 流程均未执行

### 2.2 DeepScientist（`git-full`）

- 路径：`oss/full/ResearAI__DeepScientist`
- HEAD：`b36624417f0c6b8238ec02db37b94d6db2faa5b0`，branch `main`，提交时间 2026-06-28
- 许可证：Apache-2.0（根 `LICENSE`）
- 已核对内容：
  - `docs/en/14_PROMPT_SKILLS_AND_MCP_GUIDE.md`：逐轮 prompt 组装、prompt mirror 自动刷新与 `prompt_versions` 备份；
  - `docs/en/07_MEMORY_AND_MCP.md`：`memory` / `artifact` / `bash_exec` 的职责边界；
  - `src/skills/*/SKILL.md`：21 个阶段技能；
  - `src/deepscientist/artifact/guidance.py`：按阶段给出下一技能/动作建议。
- 用途：作为“L2 持久工作区 + 隐式 prompt 变更”的对照；其自更新**没有**我们的 EV/隐藏评测/lease 门。
- 未运行：未启动 daemon、未跑任何 quest

### 2.3 AI-Scientist-v3（`git-full`）

- 路径：`oss/full/SakanaAI__AI-Scientist-v3`
- HEAD：`df8313889a004f8a44a472e19a833cd547bb828a`，branch `main`，提交时间 2026-10-18
- 许可证：Apache-2.0
- 回退：`_zip/SakanaAI__AI-Scientist-v3` 是同一 commit 的完整工作树 ZIP（README 哈希已核对）
- 用途：单轮 run 内 Docker/coding-agent/rubric 对照；不把其效果当我们的结果

### 2.4 CycleResearcher（`git-full` + 回退快照）

- 路径：`oss/full/zhu-minjun__Researcher`
- HEAD：`8c1b253092f3f41b3efc414fb189004855bb49f8`，branch `main`，提交时间 2026-03-05
- 许可证：**CycleResearcher License**（基于 Mistral AI Research License；要求注册/研究用途/非商业/披露，禁止未披露投稿与再分发）
- 使用限制：**只读对照，不复用代码/模型/权重，不打包，不再分发**
- 回退：`_zip/zhu-minjun__Researcher` 是同一 commit 的完整工作树 ZIP（`readme.md` 哈希已核对）

### 2.5 其余完整工作树（`tree-snapshot`）

这些目录有完整工作树，但**没有 `.git`**；逐仓元数据在 `_zip/<name>.meta.json`，汇总在 `_zip/archives.json`。

| 仓库 | Commit | 文件数 | 校验 |
| --- | --- | --- | --- |
| gpt-researcher | `3582a68` | 841 | commit 由 GitHub API 回填；无子模块/LFS |
| InternAgent | `fa8c3ee` | 1829 | README 哈希与 commit 匹配；子模块未拉 |
| AgentLaboratory | `d9017d9` | 35 | README 哈希与 commit 匹配 |
| Biomni | `400c1f3` | 231 | README 哈希与 commit 匹配 |
| AutoResearchClaw | `be4ba47` | 756 | commit 由 API 回填；无子模块/LFS |
| ARIS | `23745b6` | 752 | commit 由 API 回填；无子模块/LFS |
| AutoResearch | `21f5912` | 221 | 与旧快照 commit 一致 |
| RSI-Anything | `8ba44cd` | 573 | 与旧快照 commit 一致 |
| OpenRSI-Index | `12e10fd` | 1569 | commit 由 API 回填；无子模块/LFS |
| AutoSci | `f676a03` | 286 | commit 由 API 回填；无子模块/LFS |

> 未逐文件做哈希比对；`README.md` 匹配只证明快照与 commit 的主文档一致，不证明每个二进制/LFS 对象都在。ZIP 归档不含 `.git`、子模块内容和 LFS 实体。

## 3. 中断与未完成

### 3.1 GPT Researcher（`partial`）

- 路径：`oss/full/_partial/assafelovic__gpt-researcher`
- 现象：只有 21 MB `.git` 对象，没有完整工作树；不能当完整仓库使用
- 处理：保留为“中断证据”；由 `scripts/clone-research-repos.sh` 重新拉到 `oss/full/assafelovic__gpt-researcher`，成功后再清理本目录

### 3.2 未完成的仓库

`HKUDS/AI-Researcher`（工作树 901.4 MB；归档下到 263 MB 后停止，见 §3.4）。

- 原因：完整 git clone 与 ZIP 归档都受 `github.com`/`codeload` 速率影响；该仓库的大头是 examples GIF 与数据集，不是代码
- 原则：能拿到 `.git` 的走 `git-full`；拿不到时先落 `tree-snapshot` 并标明，不写“完整 clone”
- 继续命令：`bash scripts/clone-research-repos.sh`（全量、无 `--depth`、无 `--filter`、递归子模块、LFS pull）

### 3.3 InternAgent 的子模块

- 父仓库主树已完整（`fa8c3ee`，README 哈希与上游一致），但 `sci_tasks/` 是 git submodule，指向 `InternScience/ResearchClawBench` @ `9b5288e`；
- 该子仓库上游约 **1.1 GB**，本轮只拉了约 140 MB 后停止，未完成，也没有把半个 ZIP 当完整内容；
- 影响：InternAgent 的 benchmark 任务数据不在本地；代码结构、planner/memory 等主树内容仍可读；
- 需要时单独拉：`curl -L -o ResearchClawBench.zip https://codeload.github.com/InternScience/ResearchClawBench/zip/9b5288e3abe660bf1c1e4bcec57f474e6e1c7ce5`，或 `git clone --recurse-submodules https://github.com/InternScience/InternAgent.git`。

### 3.4 AI-Researcher 为什么停在 263 MB

- 目标 commit：`f9a6f8480860c193afff600eeffe3defcee8a978`（`main`，GitHub 归档 URL 已固定）
- 工作树总量：**901.4 MB / 1464 blobs**；主要不是代码：
  - `examples/hgcl/scrolling_code.gif` 91.9 MB
  - `examples/dccf/scrolling_code.gif` 75.3 MB
  - `examples/rotation_vq/scrolling_code.gif` 73.1 MB
  - `examples/gnn_difformer/scrolling_code.gif` 67.9 MB
  - `examples/gnn_nodeformer/scrolling_code.gif` 63.1 MB
  - `examples/fsq/scrolling_code.gif` 62.9 MB
  - `benchmark/process/dataset_candidate/**/*.pkl|*.npz` 多个 32 MB 数据文件
- 处理：归档下到 263 MB 后主动停止，**没有把 `.part` 当完整内容**；`_partial/` 里只有早期中断的 `.git` 对象。
- 如确实需要完整副本：`curl -L -o AI-Researcher.zip https://codeload.github.com/HKUDS/AI-Researcher/zip/f9a6f8480860c193afff600eeffe3defcee8a978`，或 `git clone --recurse-submodules https://github.com/HKUDS/AI-Researcher.git`（需预留 ≥1 GB）。

## 4. 许可证与分发纪律

1. **本地只读**：`oss/full/` 已加入根 `.gitignore`，不提交、不随站点发布、不再分发。
2. **逐仓核对**：本表许可证只代表根 LICENSE 的当前文本；复用任何文件前重新核对文件头/第三方声明。
3. **禁止混用**：
   - CycleResearcher：不复用、不打包、不再分发；
   - 无许可证仓库（AI-Researcher）：不复制代码进产品；
   - `NOASSERTION`（InternAgent）：先查清条款；
   - CC BY-NC 技能包（`oss/Academic-Research-Skills-curated`）：只读/对照，不进商业交付。
4. **不把 star 数当质量/效果证据**；不把外部仓库的效果数字写成本项目结果。

## 5. 复核命令

```bash
# 是否真的有完整历史
git -C oss/full/<repo> rev-parse --is-shallow-repository   # 应为 false
git -C oss/full/<repo> log -1 --format='%H %ci %s'
git -C oss/full/<repo> submodule status
git -C oss/full/<repo> lfs ls-files

# 快照是否有 .git（没有则不能称 clone）
test -d oss/full/_zip/<repo>/.git && echo git || echo tree-snapshot

# 全量重拉（网络可用时）
bash scripts/clone-research-repos.sh
```

> 本清单是**证据状态**，不是“所有仓库都已完整克隆”的声明。未完成项保持 ⏳/⚠️，直到 `.git` 或完整工作树与上游 commit 核对通过。
