# 组会准备：FlashRSI 跑通 + Harness² 理解 + 与科研智能体进展对齐

> 用途：下一次组会前，把老师布置的两项任务（FlashRSI 快速跑通、Harness² 基本了解）变成可展示的进度，并和我们已有的科研智能体工作接上。
> 状态基线：2026-11-18。本机已做过的真实探查都写在下面，没跑通的地方明确写"未跑通/阻塞点"，不冒充。

---

## 0. 会前要交付的三样东西

1. **跑通证据**：一条最小 FlashRSI 实验的完整产物（runs/<...>/result.json、end-summary.md、snapshots/、trajectories/），以及复现命令。
2. **一页对比**：FlashRSI 优化的是什么（harness）、我们系统优化的是什么（证据闭合 + 研究执行 + 受治理自改进），两者如何互补。
3. **一个下一步实验提案**：用 FlashRSI 的 benchmark 化评估去测"科研任务执行"这一层，组会上讨论可行性与成本。

---

## 1. 老师任务拆解与验收定义

| 任务 | 验收定义（建议在组会上这么说） |
| --- | --- |
| A. FlashRSI 快速跑通 | 环境就绪；能跑一次最小 RSI 实验；能解释产物（Snapshot / trajectory / result.json）；能 evaluate 一个 Snapshot |
| B. Harness² 基本了解 | 能讲清 harness / harnessing、两级递归、Propose–Probe–Compose、improvement harness；能说明它与 FlashRSI、与我们仓库的关系 |

注意：两项任务不是同一个项目——FlashRSI 是实验台（13 RSI 算法 / 31 benchmark / 7 harness），Harness² 是另一个团队的递归 harness 框架（我们仓库已 vendored 为自进化引擎）。

---

## 2. 本机当前进度（真实探查）

### 2.1 已经能做的

- FlashRSI-main 已有 .venv（Python 3.12），flashrsi 包已安装；
- flashrsi --help 正常（run / evaluate 两个子命令）；
- 配置预检通过（不需要 Docker）：
    python -m flashrsi run --config examples/quickstart.yaml --prepare-only --output-dir runtime_data/flashrsi-prepare
  产物：runtime_data/flashrsi-prepare/skillopt-miniagent-searchqa-<timestamp>/config.yaml（redacted）；
- 示例数据存在：FlashRSI-main/examples/data/quickstart.jsonl（约 3.3 KB）。

### 2.1b 已有一次 L1 最小端到端记录（不是本轮）

design/121 记录了 2026-11-16 的一次 FlashRSI 本地上扩展跑通，按等级划分：

| 级别 | 定义 | 状态 |
| --- | --- | --- |
| L1 最小端到端 | 官方代码真跑一圈演化：算法→harness→评分→选择→产物 | ✅ 有实物、可对账（12/12 turn、候选快照、accepted=false 平局拒收） |
| L1.5 效应演示 | 基线下有“被采纳的改进/涨分” | ❌ 未达成（题池饱和） |
| L2 上游官方路径 | Docker + 外部模型 API + 31 基准原生 | ❌ 未验证 |
| L3 受治理接入 | 进 ExecPort/claim/closure/lineage | ❌ 未接入 |

**所以组会最诚实的说法是：L1 已达成过一次（有记录），L2 仍卡 Docker；不要笼统说“跑通了”。** 若本地 L1 产物还在，现场展示它比口头说更有力；若产物不在，就以 design/121 的表格 + 本轮 prepare-only/test_algorithm 证据说明。

### 2.2 当前阻塞点（跑不通的真正原因）

    python -m flashrsi run --config examples/quickstart.yaml --check-only
    -> flashrsi: error: Install Docker CLI and start a Linux daemon; see README.md

原因（已读源码确认）：flashrsi/_startup.py 的 _requires_docker：
- 容器类 benchmark（Harbor/terminal_bench/swe_bench/hotpotqa/tau2 等）需要 Docker；
- searchqa / math / aime / bbeh / supergpqa / nq / triviaqa / musique / twowiki 属于"supplied context"，同样需要 Docker 提供上下文容器。

本机现状：
- docker CLI 不在 PATH（where docker 失败），Docker Desktop 未安装；
- WSL2 有 Ubuntu（Running，版本 2），可作为 Docker Engine 的载体；
- 上游测试冒烟：pytest tests/test_cli_args.py tests/test_benchmark_harness_contract.py -> 35 项里 1 项失败（webshop 缺 execution contract，是上游自身不一致，与我们的运行无关）。

结论：**框架本身能启动、能准备配置；一次真实 evolution 卡在 Docker**。组会前优先解决 Docker，而不是换框架。

---


## 2.3 不用 Docker 能跑到什么程度（实测结论）

**官方 CLI 跑任何内置任务都需要 Docker**，原因不是配置问题：

- flashrsi/_startup.py 的 _requires_docker：22 个容器类 benchmark + 9 个 supplied-context benchmark（searchqa/math/aime/bbeh/supergpqa/nq/triviaqa/musique/twowiki）= 31 个内置任务全部命中；
- 试过自定义 benchmark 名（benchmark.name=local_qa）：CLI 直接拒绝——Unsupported benchmark，只接受那 31 个名字。

**无 Docker 仍然可以做的三件事**（都不等于“跑通一个任务”）：

1. `--prepare-only`：生成脱敏配置目录（已实测成功）；
2. `--help` / 参数校验 / 配置 schema：已实测；
3. **框架级 evolution 回路**：tests/test_algorithm.py 的 20 项测试在 in-memory benchmark + 确定性 worker 上全部通过（无 Docker、无模型调用）：

       .venv/Scripts/python.exe -m pytest tests/test_algorithm.py -q
       -> 20 passed

   这能证明 Propose→Evaluate→Snapshot 选择回路本身可运行，但**不是 benchmark 任务结果**，组会上必须这样说明。

**结论**：

- 官方 31 个 benchmark 路径（L2）= 只能装 Docker；
- 但“跑通一次演化”不必依赖官方 benchmark：design/121 的本地扩展 localqa 已达成 **L1**（12/12 turn、候选快照、平局拒收），本轮又用 test_algorithm 20 项证明回路可跑；
- 组会优先讲 L1 证据 + L2 阻塞与计划；若要补 L2，装 Docker（WSL Engine 或 Docker Desktop）后用 §4 命令；
- 不建议为赶组会临时改 FlashRSI 源码造一个 benchmark——它不能替代官方路径，也没有可比性。

## 3. 跑通路线（按推荐顺序）

### 方案 A（推荐）：WSL2 里装 Docker Engine

在管理员 PowerShell / Ubuntu 终端执行（大致）：

    wsl -d Ubuntu
    sudo apt update && sudo apt install -y docker.io
    sudo service docker start
    docker run --rm hello-world

然后让 Windows 侧能调用 docker（二选一）：
- 在 WSL 里完成所有 FlashRSI 运行（推荐，Linux 原生 + 路径一致）；
- 或把 /usr/bin/docker 暴露到 Windows PATH / 用 Docker Desktop 的 WSL 集成。

验证：

    docker info
    # 看到 Server Version 即成功

### 方案 B：Docker Desktop

安装 Docker Desktop，启用 WSL integration（Ubuntu），等 docker info 正常。

### 方案 C（兜底，不冒充跑通）

如果组会前装不上 Docker：
- 展示 prepare-only 产物 + --help + 上游测试冒烟；
- 明确说"真实 evolution 未跑，阻塞在 Docker 环境，已定位到源码检查点"；
- 给出方案 A 的预计耗时（30–60 分钟）与风险（企业网络/权限）。

---

## 4. FlashRSI 最小 run 命令（Docker 就绪后）

在 FlashRSI-main 目录下（WSL 或 Windows 均可，注意路径）：

    # 1) 配置模型供给（示例用 AutoDL 兼容端点；按实际填写）
    export TARGET_API_KEY="<key>"
    export WORKER_API_KEY="<key>"

    # 2) 最小实验：skillopt 算法 + searchqa benchmark + miniagent harness
    flashrsi run       --algorithm skillopt       --benchmark searchqa       --agent-harness miniagent       --model DeepSeek-V4.1-Flash-1017       --worker-model DeepSeek-V4.1-Flash-1017       --set agent.llm.base_url="https://www.autodl.art/api/v1"       --set agent.llm.api_key="$TARGET_API_KEY"       --set algorithm.worker.llm.base_url="https://www.autodl.art/api/v1"       --set algorithm.worker.llm.api_key="$WORKER_API_KEY"       --output-dir runs/quickstart

或直接用 YAML：

    flashrsi run --config examples/quickstart.yaml

（YAML 里 api_key/base_url 是 null，需要先填或 --set 覆盖；容器要能访问模型端点）

### 预期产物

    runs/skillopt-miniagent-searchqa-<timestamp>/
      config.yaml            # 实际配置（脱敏）
      snapshots/             # 候选 harness 资源与血缘
      trajectories/          # target 轨迹、worker 调用、选择记录
      artifacts/harbor/      # 容器产物与原生日志（若适用）
      result.json            # 选中的 Snapshot 与最终测试结果
      end-summary.json       # 机器可读摘要
      end-summary.md         # 人读摘要

### 评估一个 Snapshot

    flashrsi evaluate --config examples/quickstart.yaml       --snapshot runs/<run-dir>/snapshots/<snapshot-id>.json

---

## 5. Harness² 基本理解（组会能讲的三层）

来源：harness2-main/README.md（arXiv 2610.14224，Apache-2.0）。

1. **概念**：harness = 模型之外让它成为 agent 的系统（prompts、tools、memory、skills、orchestration）；harnessing = 优化这个系统；模型权重固定。
2. **两级递归**：
   - task-level：对当前任务做 Propose–Probe–Compose（提改动 → 探测行为差异 → 组合成改进 harness），不依赖 ground-truth 反馈；
   - harnessing-level：把已采纳的 harness 与经验教训写进持久 improvement harness，指导下一次任务。
3. **工程形态**：支持并行/顺序递归、OpenCode/Codex executor，benchmark 为 JobBench / LAB / WorkBuddy-Bench；本地 demo 不需要模型凭证：

    uv venv --python 3.12 .venv
    source .venv/bin/activate
    uv pip install -e '.[render]'
    harness2-demo --output runs/demo --k 2

**与我们仓库的关系**：harness2-main 已 vendored，modules/rsi 的自进化控制面（候选/租约/世代/回滚）就是围绕它做的治理层；但我们的 SEPC 边界是：只改 harness，不改模型权重，Claim/证据/签名仍人签。

**与 FlashRSI 的关系**：FlashRSI 是"多算法/多 harness/多 benchmark 的统一实验台"；Harness² 是一类递归 harnessing 方法/框架。组会上不要把两者混成同一个东西。

---

## 6. 与科研智能体现有进展的对齐（可讲的真实事实）

来自本仓库 design/109、111、117 与真实运行：

| 项 | 我们的真实读数 |
| --- | --- |
| ESE 全链（真实 API） | 8 篇全文、6198 span、3 候选；创新评审；中文初稿 9401 汉字 / 73 引用；审计 ready_for_human_review |
| 前沿语料扩展 | 24 篇 / 15045 span / 6 候选（pipeline --max-candidates 6） |
| 证据治理 | span→claim→closure→lineage；G1/G2/S5b/G5 人签；无自动签名 |
| 自改进候选 | 记忆图 + 6 条 durable 失败 + 冻结 held-out rubric（A 12/14；B n=4 +1.25，underpowered）+ R1/R2 配方候选 |
| 已修复的系统缺陷 | S1b 网关断点、论文写作静默回退、覆盖率假饱和、候选上限写死、创新 plan 校验误杀 ESE |

**对比一句话**：FlashRSI 优化"模型外的执行系统"并以 benchmark 分数作为信号；我们优化"研究过程的可信与可签署"，以证据闭合、判定消费和 held-out 研究任务作为信号。两者可以叠加：把"科研任务执行"当 harness，用 FlashRSI 的 benchmark 化评估来测。

---

## 7. 组会汇报结构（15–20 分钟）

1. **结论先行**（1 页）：FlashRSI 已装好、配置可跑、真实 evolution 卡在 Docker（已定位）；Harness² 已理解并和我们的 rsi 控制面对上；我们自己的 ESE 全链有真实读数。
2. **跑通证据**（2–3 页）：命令、prepare-only 目录、docker 阻塞日志、上游测试 35/36；Docker 方案与预计时间。
3. **FlashRSI 是什么**（2 页）：13/31/7、一次 run 的产物树、Snapshot/evaluate、与我们 benchmark 的差异。
4. **Harness² 是什么**（2 页）：两级递归 + Propose–Probe–Compose + improvement harness；固定权重；与我们 rsi 模块的边界。
5. **我们的进展**（3 页）：design/109 三主张（证据治理 / ESE 执行 / 自改进候选）+ design/111 全链读数 + design/117 宽度实验；明确哪些是机制、哪些是真实读数、哪些还没做。
6. **下一步提案**（1–2 页）：FlashRSI 跑通后的第一个实验——用 benchmark harness 优化"科研任务执行"，与我们的 held-out rubric 对照；需要老师确认的 3 个问题（见 §9）。
7. **风险与备选**（0.5 页）。

---

## 8. 会前 checklist 与时间表

| 时间 | 动作 | 完成标准 |
| --- | --- | --- |
| T-3 天 | WSL 装 Docker Engine / 验证 docker info | hello-world 成功 |
| T-2 天 | 配置 AutoDL key，跑通最小 run（skillopt/searchqa/miniagent） | runs/.../result.json 存在 |
| T-1 天 | evaluate 一个 Snapshot；整理产物截图与命令 | 能复现同一命令 |
| 当天 | 按 §7 排练一遍；准备 Docker 失败时的兜底页 | 15 分钟讲完 |

---

## 9. 需要老师确认的问题（组会直接问）

1. FlashRSI 的 benchmark 选择：先用 searchqa 跑通即可，还是必须对齐某个具体 benchmark（HotpotQA / SearchQA / MATH）？
2. 模型供给：用外部 API（DeepSeek/AutoDL）还是学校/组内端点？容器出网是否允许？
3. 是否把"科研任务执行"作为 harness 层接进 FlashRSI 做评估？这决定后续是"复现 FlashRSI"还是"用 FlashRSI 做我们的实验台"。

---

## 10. 附：本机证据（可现场演示）

- FlashRSI CLI：FlashRSI-main/.venv/Scripts/python.exe -m flashrsi --help
- 配置预检产物：FlashRSI-main/runtime_data/flashrsi-prepare/skillopt-miniagent-searchqa-20261118-*/config.yaml
- Docker 阻塞：flashrsi run --config examples/quickstart.yaml --check-only 的报错原文
- 上游测试：pytest tests/test_cli_args.py tests/test_benchmark_harness_contract.py（35 项通过、1 项 webshop contract 失败）
- Harness²：harness2-main/README.md；本仓库 modules/rsi/SPEC.md
- 我们的 ESE 全链：design/111、design/117；真实产物在 runtime_data/ese-fullrun-20261118、runtime_data/ese-frontier6-20261118（本机）

---

## 11. 一句话总结

组会上要传达的是：**FlashRSI 已就绪到"只差 Docker"，Harness² 已能讲清两级递归并和我们的 rsi 控制面对齐；同时我们自己的科研智能体已经有真实 ESE 全链读数与证据治理边界**。下一步不是再装更多框架，而是把"科研任务执行"接进 FlashRSI 的评估体系做一次对照实验。
