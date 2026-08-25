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
TEAL, LAVENDER, MAUVE, GOLD = "#94e2d5", "#b4befe", "#cba6f7", "#f9e2af"

# Contest names are host-university codes; "IUPC" is redundant on nearly every
# row (it's the tournament format, not the identity), so drop it from the
# x-axis label and keep it in the full name only for the hover-free legend.
DROP_SUFFIX = " IUPC"


def load_rows():
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


def short_label(contest):
    return contest[: -len(DROP_SUFFIX)] if contest.endswith(DROP_SUFFIX) else contest


def main():
    rows = load_rows()
    done = [r for r in rows if r["rank"].strip()]
    pending_count = len(rows) - len(done)

    labels = [f"{short_label(r['contest'])} '{r['year'][-2:]}" for r in done]
    ranks = [int(r["rank"]) for r in done]

    plt.rcParams["font.family"] = "monospace"
    fig, ax = plt.subplots(figsize=(7.6, 4.4), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    x = list(range(len(labels)))

    # subtle gradient fill under the line — a bit of visual flair, still
    # readable against the dark background
    ax.fill_between(x, ranks, max(ranks) + 10, color=TEAL, alpha=0.08, zorder=1)

    ax.plot(x, ranks, color=TEAL, linewidth=2, zorder=3)

    top20_i = [i for i, r in enumerate(ranks) if r <= 20]
    other_i = [i for i in x if i not in top20_i]
    if other_i:
        ax.scatter([x[i] for i in other_i], [ranks[i] for i in other_i],
                   color=TEAL, s=42, zorder=4, edgecolors=BG, linewidths=1.3)
    if top20_i:
        ax.scatter([x[i] for i in top20_i], [ranks[i] for i in top20_i],
                   color=GOLD, s=64, zorder=4, marker="D", edgecolors=BG, linewidths=1.1)

    best_i = ranks.index(min(ranks))
    ax.scatter([x[best_i]], [ranks[best_i]], color=MAUVE, s=150, zorder=5, marker="*", edgecolors=BG, linewidths=0.8)
    ax.annotate(f"best \u2014 rank {ranks[best_i]}", (x[best_i], ranks[best_i]),
                textcoords="offset points", xytext=(0, 15), ha="center", fontsize=9, color=MAUVE)

    for xi, yi in zip(x, ranks):
        if xi == best_i:
            continue
        ax.annotate(f"{yi}", (xi, yi), textcoords="offset points", xytext=(0, 14),
                    ha="center", fontsize=8, color=SUBTEXT)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=SUBTEXT, fontsize=8.3, rotation=40, ha="right")
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.invert_yaxis()
    ax.set_ylabel("rank", color=SUBTEXT, fontsize=9.5)
    ax.tick_params(axis="y", colors=SUBTEXT, labelsize=8.5)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Onsite (representing IUT)", color=TEXT, fontsize=12, fontfamily="monospace", loc="left", pad=10)

    if top20_i:
        ax.text(0.0, 1.12, f"\u25c6 top 20", transform=ax.transAxes, ha="left",
                fontsize=8, color=GOLD, style="italic")
    if pending_count:
        ax.text(1.0, 1.12, f"+{pending_count} pending",
                transform=ax.transAxes, ha="right", fontsize=8.5, color=LAVENDER, style="italic")

    fig.tight_layout(pad=1.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG, format="svg")
    print(f"wrote {OUT} ({len(done)} completed, {pending_count} pending)")


if __name__ == "__main__":
    main()
