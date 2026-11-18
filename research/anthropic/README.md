# Anthropic 官方公开资料快照

> 下载日期：2026-10-25  
> 用途：对照 Anthropic 的 Agent Loop / subagent / skills / Agent SDK 实践，给本仓库的单 Loop 与 Review Pack 设计提供可核验底本。  
> 注意：这是**本地参考资料**，不是本项目的运行时依赖；不要把第三方代码当作我们的实现或结果。

## 1. 文章

| 文件 | 来源 | 说明 |
| --- | --- | --- |
| `articles/subagents-loop.html` | https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop | 2026-10 抓取的官方文章 HTML；标题 *Building agents: When to fold subagents into your main agent loop*；版权归 Anthropic，仅作本地阅读 |

文章主张（厂商 blog，非同行评审）：

- 默认单 Agent Loop + 渐进披露 skills/tools；subagent 只在上下文膨胀、并行且用完即弃、工具/指令冲突时保留；
- 迁移要评估先行，一次折叠一个；折叠后变差就保留 subagent；
- 工具按用户意图分组，工具定义过多会退化；记忆最终更接近 RAG；
- 不能把厂商自报的“更快/更好”当成我们的实测结果。

## 2. 代码快照

| 本地目录 | 上游 | Commit | License | 大小 | 用途 |
| --- | --- | --- | --- | --- | --- |
| `repos/single-agent-loop-kit` | https://github.com/anthropics/single-agent-loop-kit | `c43796287b83bec847db923f07131d1cc8de750d` | Apache-2.0 | ~1.7 MB | **主参考**：reference loop、audit/fold skill、eval runner、support-desk 示例 |
| `repos/claude-agent-sdk-python` | https://github.com/anthropics/claude-agent-sdk-python | `0e89b298e771259378a6cd3734e00d323dff5703` | MIT | ~2.4 MB | Agent SDK 的 query/client、tools、hooks、permissions、sessions 设计 |
| `repos/skills` | https://github.com/anthropics/skills | `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | 混合：多数 Apache-2.0；docx/pdf/pptx/xlsx 为 source-available | ~13 MB | Agent Skills 规范、SKILL.md 结构、skill-creator、渐进披露示例 |
| `repos/claude-quickstarts` | https://github.com/anthropics/claude-quickstarts | `930ad10bb2e21a9ef97fe1a88d2037e18a24465c` | MIT | ~9.7 MB | 客户支持/研究等端到端 starter 结构 |

### 明确没有整仓下载的资料

- `anthropics/claude-cookbooks`：API 报告约 227 MB，未整仓下载；需要时按目录 sparse 获取；
- `anthropics/evals`：API 报告约 103 MB，未整仓下载；
- `anthropics/sandbox-runtime`：约 12 MB，未下载；与当前“无工具执行”的边界无关；
- `anthropics/claude-code`：本仓库已有本地 `claude-code-main/` 快照，未重复下载。

## 3. 使用边界

- `single-agent-loop-kit` 是 **reference implementation, not maintained**；我们只借它的 loop/budget/write-gate/eval 结构，不把它当作生产依赖。
- `skills` 仓库不是统一开源：`docx/pdf/pptx/xlsx` 是 source-available，不能并入商业交付物；导入时仍要按 `modules/skills/SPEC.md` 的 untrusted/manual 规则处理。
- 文章和代码的版权/许可证不因“下载到本地”而改变；对外发布只放我们的实现与引用，不复制第三方大段内容。
- 厂商文章里的性能/成本数字不是我们的实验结果；我们的 eval 必须自己跑。
- 环境差异：`single-agent-loop-kit` 的 48 个测试在 **Python 3.12 全部通过**；本仓库默认 Python 3.8 下因 `Path.is_relative_to`（3.9+）出现 3 failures / 8 errors。若借它的代码，必须先适配到 3.8 或把 runtime 升到 3.10+。

## 4. 对应到本仓库

- 我们的审计与迁移计划在 `single-loop/PLAN.md`、`single-loop/inventory.tsv`；
- 已落地的“subagent as tool”最小实现：前端 `/review` Review Pack（`apps/web/src/domain/reviewPack.ts`）与 `review-pack` 卡；
- 已落地的 harness 守卫：已签 claim 时禁止 `/run` 与启动/单步全自动覆盖签名；
- 下一步：按 kit 的 Step 1 建 10–20 条端到端 eval，再做第一次 fold（S2–S3 假设收敛）。

## 5. 关键参考文件

- `repos/single-agent-loop-kit/reference_loop/loop.py`：单 Loop、并行 tool batch、skills on demand、tool search、budget、write gate、verifier；
- `repos/single-agent-loop-kit/skill/steps/00-audit.md`：subagent inventory 与 verdict 规则；
- `repos/single-agent-loop-kit/skill/steps/04-as-tool.md`：把保留的 subagent 包成 tool 的完整流程；
- `repos/single-agent-loop-kit/skill/templates/subagent_response.schema.json`：structured subagent result；
- `repos/single-agent-loop-kit/examples/support-desk/evals/run_eval.py`：golden tasks、action grading、Wilson CI、fake model；
- `repos/claude-agent-sdk-python/README.md`：query/client、allowed/disallowed tools、permissions、hooks、sessions；
- `repos/skills/spec/agent-skills-spec.md`：Agent Skills 规范。
