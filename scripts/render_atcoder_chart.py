"""
Reads data/cache/atcoder_history.json (written by fetch_atcoder_history.py)
and renders assets/img/atcoder_chart.svg. If there's no rated history yet
(or the fetch never succeeded), draws a clean placeholder instead of a broken
or empty chart.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "atcoder_history.json"
OUT = ROOT / "assets" / "img" / "atcoder_chart.svg"

BG, GRID, TEXT, SUBTEXT = "#181825", "#313244", "#cdd6f4", "#a6adc8"
BLUE, MAUVE, LAVENDER = "#89b4fa", "#cba6f7", "#b4befe"


def placeholder(ax, message):
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.text(0.5, 0.55, message, ha="center", va="center", color=SUBTEXT,
            fontsize=11, fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.4, "run scripts/fetch_atcoder_history.py", ha="center", va="center",
            color=SUBTEXT, fontsize=8.5, fontfamily="monospace", alpha=0.6, transform=ax.transAxes)


def main():
    history = json.loads(CACHE.read_text()) if CACHE.exists() else []

    plt.rcParams["font.family"] = "monospace"
    # Height set to 4.4 with pad=1.6 to match onsite_chart.py SVG canvas dimensions exactly
    fig, ax = plt.subplots(figsize=(6.3, 4.4), dpi=200)
    fig.patch.set_facecolor(BG)

    if not history:
        placeholder(ax, "no rated AtCoder contests yet")
        fig.tight_layout(pad=1.6)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT, facecolor=BG, format="svg")
        print(f"wrote {OUT} (placeholder, no data)")
        return

    ax.set_facecolor(BG)
    ratings = [h["NewRating"] for h in history]
    x = list(range(len(ratings)))

    # Subtle area gradient fill matching the onsite chart aesthetic
    min_fill = max(0, min(ratings) - 40)
    ax.fill_between(x, ratings, min_fill, color=BLUE, alpha=0.08, zorder=1)

    ax.plot(x, ratings, color=BLUE, linewidth=2, zorder=3)
    ax.scatter(x, ratings, color=BLUE, s=42, zorder=4, edgecolors=BG, linewidths=1.2)

    # Peak rating callout
    peak_i = ratings.index(max(ratings))
    ax.scatter([x[peak_i]], [ratings[peak_i]], color=MAUVE, s=150, zorder=5, marker="*", edgecolors=BG, linewidths=0.8)

    if peak_i == len(ratings) - 1:
        ax.annotate(f"peak & current \u2014 {ratings[peak_i]}", (x[peak_i], ratings[peak_i]),
                    textcoords="offset points", xytext=(0, 14), ha="center", fontsize=9, color=MAUVE, fontweight="bold")
    else:
        ax.annotate(f"peak \u2014 {ratings[peak_i]}", (x[peak_i], ratings[peak_i]),
                    textcoords="offset points", xytext=(0, 14), ha="center", fontsize=9, color=MAUVE, fontweight="bold")
        ax.annotate(f"current \u2014 {ratings[-1]}", (x[-1], ratings[-1]),
                    textcoords="offset points", xytext=(0, -16), ha="center", fontsize=8.5, color=SUBTEXT)

    # Clean axes typography & framing
    ax.set_xticks([])
    if len(x) > 1:
        ax.set_xlim(-0.5, len(x) - 0.5)
    ax.set_ylabel("rating", color=SUBTEXT, fontsize=9.5)
    ax.tick_params(axis="y", colors=SUBTEXT, labelsize=8.5)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)

    # Title & Subtitle styling parallel to onsite_chart
    ax.set_title("AtCoder", color=TEXT, fontsize=12, fontfamily="monospace", loc="left", pad=10)
    ax.text(1.0, 1.12, f"{len(history)} rated contests", transform=ax.transAxes,
            ha="right", fontsize=8.5, color=LAVENDER, style="italic")

    fig.tight_layout(pad=1.6)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=BG, format="svg")
    print(f"wrote {OUT} ({len(history)} contests)")


if __name__ == "__main__":
    main()