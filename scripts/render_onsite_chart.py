"""
Reads data/onsite_contests.csv and renders assets/img/onsite_chart.svg.
Rows with a blank rank are treated as pending/upcoming and excluded from the
line (but counted in the "N more scheduled" annotation).
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "onsite_contests.csv"
OUT = ROOT / "assets" / "img" / "onsite_chart.svg"

BG, GRID, TEXT, SUBTEXT = "#181825", "#313244", "#cdd6f4", "#a6adc8"
TEAL, LAVENDER, MAUVE = "#94e2d5", "#b4befe", "#cba6f7"


def load_rows():
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


def main():
    rows = load_rows()
    done = [r for r in rows if r["rank"].strip()]
    pending_count = len(rows) - len(done)

    labels = [f"{r['contest']}\n'{r['year'][-2:]}" for r in done]
    ranks = [int(r["rank"]) for r in done]

    plt.rcParams["font.family"] = "monospace"
    fig, ax = plt.subplots(figsize=(6.3, 4.4), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    x = list(range(len(labels)))
    ax.plot(x, ranks, color=TEAL, linewidth=2, zorder=3)
    ax.scatter(x, ranks, color=TEAL, s=45, zorder=4, edgecolors=BG, linewidths=1.3)

    best_i = ranks.index(min(ranks))
    ax.scatter([x[best_i]], [ranks[best_i]], color=MAUVE, s=140, zorder=5, marker="*", edgecolors=BG, linewidths=0.8)
    ax.annotate(f"best - rank {ranks[best_i]}", (x[best_i], ranks[best_i]),
                textcoords="offset points", xytext=(-38, 13), ha="center", fontsize=9, color=MAUVE)

    for xi, yi in zip(x, ranks):
        if xi == best_i:
            continue
        ax.annotate(f"{yi}", (xi, yi), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=8.5, color=SUBTEXT)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=SUBTEXT, fontsize=7.8, rotation=25, ha="right")
    ax.invert_yaxis()
    ax.set_ylabel("rank", color=SUBTEXT, fontsize=9.5)
    ax.tick_params(axis="y", colors=SUBTEXT, labelsize=8.5)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Onsite (IUT)", color=TEXT, fontsize=12, fontfamily="monospace", loc="left", pad=10)

    if pending_count:
        ax.text(1.0, 1.12, f"+{pending_count} pending",
                transform=ax.transAxes, ha="right", fontsize=8.5, color=LAVENDER, style="italic")

    fig.tight_layout(pad=1.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG, format="svg")
    print(f"wrote {OUT} ({len(done)} completed, {pending_count} pending)")


if __name__ == "__main__":
    main()
