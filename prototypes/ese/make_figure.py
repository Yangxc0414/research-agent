"""Generate the Wellspring-ESE architecture figure.

This is a design illustration, not an empirical result. Run:
    python -m prototypes.ese.make_figure
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
AMBER = "#b7791f"
AMBER_LIGHT = "#fdf3df"
RED = "#a63a3a"
RED_LIGHT = "#f9e6e6"
GRAY = "#5b6577"
GRAY_LIGHT = "#f1f3f6"
WHITE = "#ffffff"
BLUE = "#2b4f81"
BLUE_LIGHT = "#e6edf7"


def box(ax, x, y, w, h, text, fc=WHITE, ec=GRAY, size=9, bold=False, color=NAVY, radius=1.2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.25,rounding_size={0}".format(radius),
        linewidth=1.0, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2.0, y + h / 2.0, text,
        ha="center", va="center", fontsize=size,
        color=color, fontweight="bold" if bold else "normal",
        linespacing=1.35,
    )
    return patch


def arrow(ax, start, end, color=GRAY, rad=0.0, lw=1.2, style="-|>", ls="-"):
    patch = FancyArrowPatch(
        start, end,
        arrowstyle=style, mutation_scale=10,
        linewidth=lw, color=color, linestyle=ls,
        connectionstyle="arc3,rad={0}".format(rad),
        shrinkA=2, shrinkB=2,
    )
    ax.add_patch(patch)


def main():
    fig, ax = plt.subplots(figsize=(16, 10.2), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.axis("off")
    fig.patch.set_facecolor("#fbfcfe")

    ax.text(2, 60.4, "Wellspring-ESE", fontsize=20, fontweight="bold", color=NAVY)
    ax.text(2, 58.3, "面向经验软件工程的研究框架：一个内核、两类插件、一个工作区、一个元演化",
            fontsize=10.5, color=GRAY)
    ax.plot([2, 98], [57.3, 57.3], color="#d9dee8", lw=1)

    # ---------------- Base loop ----------------
    box(ax, 2, 41.8, 70, 14.6, "", fc="#f7f9fc", ec="#cfd7e6", radius=1.6)
    ax.text(4, 55.0, "ESE Base · 五阶段研究闭环（不是流水线）", fontsize=11.2,
            fontweight="bold", color=NAVY)
    ax.text(40.0, 55.0, "Design 前硬门：最难关口探针（failed → redesign / respecify）",
            fontsize=7.8, color="#8a5a12")

    stages = [
        ("Specify", "断言 + 5 威胁\n+ scope"),
        ("Design", "预注册 + 功效\n+ 冻结"),
        ("Execute", "run + 数据/代码\n/环境指纹"),
        ("Verify", "区间 + 复现\n+ 适用域"),
        ("Deposit", "人签 claim\n+ 失败图谱"),
    ]
    xs = [4.5, 17.5, 30.5, 43.5, 56.5]
    for index, ((title, sub), x) in enumerate(zip(stages, xs)):
        fc = TEAL_LIGHT if index in (0, 1) else (BLUE_LIGHT if index in (2, 3) else AMBER_LIGHT)
        ec = TEAL if index in (0, 1) else (BLUE if index in (2, 3) else AMBER)
        box(ax, x, 47.0, 11.2, 6.2, title + "\n" + sub, fc=fc, ec=ec, size=8.6, bold=False)
        if index < len(stages) - 1:
            arrow(ax, (x + 11.2, 50.1), (xs[index + 1], 50.1), color=GRAY, lw=1.4)

    # return arcs: short and shallow, legend below
    arrow(ax, (49.1, 47.0), (23.1, 47.0), color=RED, rad=-0.10, lw=1.2)
    arrow(ax, (36.1, 47.0), (23.1, 47.0), color=RED, rad=-0.08, lw=1.1)
    ax.text(4, 44.2,
            "红色回流：Verify→Design（效度威胁） · Execute→Design（操作失败） · 构念错配回到 Specify",
            fontsize=7.2, color=RED)
    ax.text(4, 43.0, "唯一 dispatcher；同一瓶颈两批无决策增量 → 独立全局重评", fontsize=7.2, color=GRAY)

    # ---------------- Workspace memory ----------------
    box(ax, 74.5, 29.5, 24, 27.3, "", fc="#f8faf9", ec="#cfe0dc", radius=1.6)
    ax.text(76.3, 55.2, "Workspace Memory · 单题长程记忆", fontsize=10.5, fontweight="bold", color=TEAL)
    items = [
        ("Claim（三轴分列）\n证据 / 复现 / 适用域", TEAL_LIGHT, TEAL),
        ("Protocol（预注册 + 冻结）\n采样 / 功效 / 分析 / 停止", BLUE_LIGHT, BLUE),
        ("Failure Atlas（durable only）\n诊断 / 重试条件 / 范围", RED_LIGHT, RED),
        ("Dataset Cards\n许可 / 抽样 / 时间切分 / 污染", AMBER_LIGHT, AMBER),
        ("NEXT_SESSION + 决策记录\n当前事实 / 未闭义务", GRAY_LIGHT, GRAY),
    ]
    y = 51.4
    for text, fc, ec in items:
        box(ax, 76.2, y, 20.7, 3.2, text, fc=fc, ec=ec, size=7.4)
        y -= 3.65

    ax.text(76.3, 31.2, "QueryPack 预算：failures 永不裁剪 > scope > datasets > papers > ideas",
            fontsize=7.0, color=GRAY)
    ax.text(76.3, 29.9, "写入准入：人签 claim / 复现结果 / durable 失败；operational 只进日志",
            fontsize=7.0, color=GRAY)

    # ---------------- Domain plugins ----------------
    box(ax, 2, 17.0, 70, 23.6, "", fc="#fbf9f6", ec="#e3d8c8", radius=1.6)
    ax.text(4, 39.7, "Domain Plugins · 二维契约：方法 × 任务（+ 数据集卡）",
            fontsize=11.2, fontweight="bold", color="#6b4b18")

    # matrix: methods x tasks, with a few registered example combinations
    methods = ["repository mining", "benchmark evaluation", "controlled experiment", "case study"]
    tasks = ["defect prediction", "LLM4Code", "code review", "flaky test"]
    combos = {(0, 0), (1, 1), (2, 2), (3, 3)}
    x0, y_top = 12.5, 37.5
    cell_w, cell_h, gap = 10.0, 1.9, 0.55
    for row, method in enumerate(methods):
        cy = y_top - row * (cell_h + gap) - cell_h
        ax.text(11.8, cy + cell_h / 2.0, method, ha="right", va="center",
                fontsize=7.2, color=GRAY)
        for col, task in enumerate(tasks):
            cx = x0 + col * (cell_w + 0.6)
            if (row, col) in combos:
                fc, ec, mark = "#fff2d8", AMBER, "●"
            else:
                fc, ec, mark = "#ffffff", "#d7cbb8", "·"
            box(ax, cx, cy, cell_w, cell_h, "", fc=fc, ec=ec, radius=0.6)
            ax.text(cx + cell_w / 2.0, cy + cell_h / 2.0, mark,
                    ha="center", va="center", fontsize=8.0, color=ec)
    for col, task in enumerate(tasks):
        ax.text(x0 + col * (cell_w + 0.6) + cell_w / 2.0, y_top + 0.25, task,
                ha="center", va="bottom", fontsize=7.2, color=GRAY)
    ax.text(12.5, 26.9, "● 已登记的示例组合（不是穷举）；空白格不是不可能，而是尚未登记",
            fontsize=7.0, color=AMBER)
    ax.text(33.0, 25.4, "同一任务可由不同方法研究：效度威胁与报告规范不同；冲突必须显式报出",
            fontsize=7.2, color=GRAY)
    ax.text(33.0, 24.0, "每个插件必须声明 cannot_support；不得创建 Claim / 签署 / 改门禁",
            fontsize=7.2, color=RED)

    # dataset cards
    box(ax, 3.0, 18.2, 67.5, 4.6,
        "Dataset Cards：name / source / license / sampling / subject_kind / known_biases / time_split / contamination_note\n"
        "LLM 数据集强制填污染说明：训练截止、重叠检测或私有留出集",
        fc=AMBER_LIGHT, ec="#d9b56a", size=7.2, color="#6b4b18")

    # ---------------- Meta evolution ----------------
    box(ax, 74.5, 4.0, 24, 23.0, "", fc="#fbf7fb", ec="#ddcfe2", radius=1.6)
    ax.text(76.2, 25.5, "Meta-evolve · 与解题循环分离", fontsize=10.5, fontweight="bold", color="#6b3f78")
    ax.text(76.2, 23.9, "慢、可回滚、由真实研究证据驱动", fontsize=7.2, color=GRAY)

    steps = [
        ("durable 失败复现", 20.6),
        ("候选改动（只改一层）", 17.6),
        ("shadow eval：≥2 held-out\n无回归 + 成本审计", 14.6),
        ("人写理由 → adopt / reject / defer", 11.6),
        ("版本 + 回滚点 + 证据", 8.6),
    ]
    for text, yy in steps:
        box(ax, 76.2, yy, 20.7, 2.4, text, fc="#f3eaf6", ec="#b99ac6", size=7.2, color="#4d2a57")
    for index in range(len(steps) - 1):
        arrow(ax, (86.55, steps[index][1]), (86.55, steps[index + 1][1] + 2.4),
              color="#8a6a99", lw=1.0)

    ax.text(76.2, 6.2, "不可触碰：claim / evidence / gate / rubric / signature / export / heldout",
            fontsize=6.8, color=RED)
    ax.text(76.2, 5.0, "没有 held-out 证据的版本号不是 RSI", fontsize=6.8, color="#6b3f78")

    # ---------------- Bottom invariants ----------------
    box(ax, 2, 2.0, 70, 12.8, "", fc="#f7f9fc", ec="#cfd7e6", radius=1.4)
    ax.text(4, 13.3, "Kernel invariants", fontsize=10.2, fontweight="bold", color=NAVY)
    ax.text(4, 11.4, "① 不创建 Claim / EA / Verdict / Signature；只算 blockers、状态、QueryPack、冲突报告。",
            fontsize=7.6, color=NAVY)
    ax.text(4, 9.7, "② 三轴不合并：supported ≠ reproduced ≠ generalizes；undecidable 永不可签。",
            fontsize=7.6, color=NAVY)
    ax.text(4, 8.0, "③ 失败先分类：operational 只进日志，durable 才进图谱；未知类型 fail-closed。",
            fontsize=7.6, color=NAVY)
    ax.text(4, 6.3, "④ 插件边界：cannot_support 非空；不得签核、不得改门禁。",
            fontsize=7.6, color=NAVY)
    ax.text(4, 4.6, "⑤ 跨域：同一内核挂数学（证明/证书）与 ESE（设计/统计/复现），领域语义由插件注入。",
            fontsize=7.6, color=NAVY)
    ax.text(4, 2.9, "⑥ 元演化不碰判定面；adopt 是人的动作，函数只给建议。",
            fontsize=7.6, color=NAVY)

    ax.text(74.5, 2.0, "设计图 · 2026-11-18 · 原型未注册", fontsize=7.0, color="#9aa3b2")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "figures", "ese")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, "ese-architecture.png")
    svg = os.path.join(out_dir, "ese-architecture.svg")
    fig.savefig(png, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(png)
    print(svg)


if __name__ == "__main__":
    main()
