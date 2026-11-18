"""Generate the two-level evolution figure (research loop + method evolution loop).

This is a *design projection*, not an implementation map: the outer loop is roadmap.
Run:
    python -m prototypes.ese.make_figure_loop
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#1f2a44"
TEAL = "#1f6f78"
TEAL_LIGHT = "#e3f2f2"
BLUE = "#2b4f81"
BLUE_LIGHT = "#e6edf7"
AMBER = "#b7791f"
AMBER_LIGHT = "#fdf3df"
RED = "#a63a3a"
RED_LIGHT = "#f9e6e6"
PURPLE = "#6b3f78"
PURPLE_LIGHT = "#f3eaf6"
GRAY = "#5b6577"
GRAY_LIGHT = "#f1f3f6"
WHITE = "#ffffff"


def box(ax, x, y, w, h, text, fc=WHITE, ec=GRAY, size=9, bold=False, color=NAVY, radius=1.0):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.25,rounding_size={0}".format(radius),
        linewidth=1.0, edgecolor=ec, facecolor=fc,
    ))
    ax.text(x + w / 2.0, y + h / 2.0, text, ha="center", va="center",
            fontsize=size, color=color, fontweight="bold" if bold else "normal",
            linespacing=1.35)


def arrow(ax, start, end, color=GRAY, rad=0.0, lw=1.2, ls="-"):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=11, linewidth=lw,
        color=color, linestyle=ls,
        connectionstyle="arc3,rad={0}".format(rad), shrinkA=2, shrinkB=2,
    ))


def main():
    fig, ax = plt.subplots(figsize=(15, 9.6), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 58)
    ax.axis("off")
    fig.patch.set_facecolor("#fbfcfe")

    ax.text(2, 56.6, "同一系统的两条循环：研究循环（已实现）与 方法演化循环（roadmap）",
            fontsize=17, fontweight="bold", color=NAVY)
    ax.text(2, 54.6, "demo 的四张图只画了内层与治理；这张图补上外层——自改进科研智能体真正缺的那一层。",
            fontsize=10.2, color=GRAY)
    ax.plot([2, 98], [53.6, 53.6], color="#d9dee8", lw=1)

    # ---------- inner loop ----------
    ax.add_patch(FancyBboxPatch((2, 27.0), 58, 24.6, boxstyle="round,pad=0.3,rounding_size=1.6",
                                linewidth=1.2, edgecolor=TEAL, facecolor="#f6fbfb"))
    ax.text(3.6, 50.4, "内层 · 研究循环（已实现：证据闭合）", fontsize=12, fontweight="bold", color=TEAL)
    ax.text(3.6, 48.0, "对单个研究问题：把结论做到可核验、可复现、可撤销", fontsize=8.4, color=GRAY)

    stages = [
        ("Specify\n断言 + 5 威胁", 4.0),
        ("Design\n预注册 + 探针", 15.0),
        ("Execute\nrun + 指纹", 26.0),
        ("Verify\n区间 + 复现", 37.0),
        ("Deposit\n人签 claim", 48.0),
    ]
    for title, x in stages:
        box(ax, x, 39.4, 9.6, 6.2, title, fc=TEAL_LIGHT, ec=TEAL, size=8.2)
    for index in range(len(stages) - 1):
        arrow(ax, (stages[index][1] + 9.6, 42.5), (stages[index + 1][1], 42.5), color=TEAL, lw=1.4)

    # return arrows inside inner loop
    arrow(ax, (46.0, 39.2), (19.8, 35.4), color=RED, rad=0.16, lw=1.1)
    ax.text(26.0, 36.0, "效度问题 → Design / Specify", fontsize=7.4, color=RED)
    ax.text(26.0, 34.4, "（当前 demo 缺这条：分析发现泄漏只能写 warning）", fontsize=7.0, color=RED)

    box(ax, 4.0, 28.6, 54.0, 4.6,
        "产物：ClaimSpec / ProtocolCard / StudyCapsule / 区间 + 复现 / signed claim / closure + lineage\n"
        "门：G1 想法 · G2 设计 · S5b 结果人签 · G5 闭包；autopilot 只在人写策略边界内代签",
        fc=WHITE, ec="#bcd7d7", size=7.6, color=NAVY)

    # ---------- outer loop ----------
    ax.add_patch(FancyBboxPatch((2, 2.0), 96, 22.6, boxstyle="round,pad=0.3,rounding_size=1.6",
                                linewidth=1.2, edgecolor=PURPLE, facecolor="#fbf7fb", linestyle=(0, (4, 2))))
    ax.text(3.6, 22.6, "外层 · 方法演化循环（roadmap：现在只有骨架，没有 held-out 研究任务）",
            fontsize=12, fontweight="bold", color=PURPLE)
    ax.text(3.6, 20.4, "对『我们怎样做研究』本身：从真实失败中改方法/插件/检查项，用留出研究任务验证，人采纳，可回滚",
            fontsize=8.4, color=GRAY)

    outer = [
        ("① 失败图谱\ndurable 失败 + 复现结果\n（当前：无）", 4.0),
        ("② 候选改动\n只改一层：base /\n方法插件 / 任务插件 / 数据卡", 22.0),
        ("③ held-out 研究任务\n≥2 个未参与设计的任务\n（当前：无）", 40.0),
        ("④ 人采纳 / 拒绝\n+ 成本审计\n（当前：rsI 只到租约）", 58.0),
        ("⑤ 版本 + 回滚点\n方法指纹（不只代码）\n（当前：世代只覆盖代码）", 76.0),
    ]
    for title, x in outer:
        box(ax, x, 10.2, 17.0, 7.6, title, fc=PURPLE_LIGHT, ec="#b99ac6", size=7.6, color="#4d2a57")
    for index in range(len(outer) - 1):
        arrow(ax, (outer[index][1] + 17.0, 14.0), (outer[index + 1][1], 14.0),
              color="#8a6a99", lw=1.3, ls=(0, (4, 2)))

    # outer return: adopted version becomes the next study's method (conceptual, no crossing arrow)
    arrow(ax, (84.5, 18.0), (84.5, 22.2), color=PURPLE, rad=0.0, lw=1.3, ls=(0, (4, 2)))
    ax.text(66.0, 19.4, "采纳后的方法 → 下一版 → 下一次研究（与内层相接）", fontsize=7.4, color=PURPLE)

    # inner -> outer evidence
    arrow(ax, (30.0, 28.0), (30.0, 18.0), color=AMBER, lw=1.4)
    ax.text(31.4, 25.6, "内层产出证据：durable 失败 / 复现结果 / 成本", fontsize=7.2, color=AMBER)

    # ---------- middle: verdict bus ----------
    box(ax, 62.0, 30.0, 34.0, 15.6, "", fc=GRAY_LIGHT, ec="#c9cfda", radius=1.4)
    ax.text(64.0, 43.6, "贯穿两层的判定总线（已有）", fontsize=10.5, fontweight="bold", color=NAVY)
    lines = [
        "verdict-ledger：三态判定 / closure blockers / lineage stale",
        "读时重算：快照只兜底，判定从产物重导出",
        "人签只留在 CLI；runtime / MCP / 前端零签名入口",
        "",
        "缺的一环：判定要能驱动『方法层』改动，",
        "而不是只驱动下一次 run 的动作。",
    ]
    y = 41.4
    for line in lines:
        ax.text(64.0, y, line, fontsize=7.6, color=NAVY if not line.startswith("缺") else RED)
        y -= 2.1

    # ---------- legend ----------
    ax.text(2.0, 0.9, "实线 = 研究/演化前向　虚线 = 演化回路（roadmap）　红 = 回流/缺口　"
                      "本图是设计投影，不是实现地图；外层五步均为 roadmap。",
            fontsize=7.6, color=GRAY)

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "figures", "ese"))
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, "double-loop.png")
    svg = os.path.join(out_dir, "double-loop.svg")
    fig.savefig(png, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(png)
    print(svg)


if __name__ == "__main__":
    main()
