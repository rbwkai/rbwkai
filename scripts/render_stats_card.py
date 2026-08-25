"""
Renders data/cache/stats.json into assets/img/gh_stats.svg — a small stats card
in the same Catppuccin Mocha palette as the banner and onsite chart. Self-hosted,
so it can't go down the way the third-party stats-card services periodically do.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "stats.json"
OUT = ROOT / "assets" / "img" / "gh_stats.svg"

BG, TEXT, SUBTEXT, MAUVE, TEAL, LAVENDER = "#181825", "#cdd6f4", "#a6adc8", "#cba6f7", "#94e2d5", "#b4befe"
LANG_COLORS = [MAUVE, TEAL, LAVENDER, "#89b4fa", "#f5c2e7", "#a6e3a1"]


def main():
    stats = json.loads(CACHE.read_text())
    langs = stats.get("top_languages", [])
    total_bytes = sum(l["bytes"] for l in langs) or 1

    # stat chips
    chips = [
        ("public repos", stats["public_repos"]),
        ("total stars", stats["total_stars"]),
        ("followers", stats["followers"]),
    ]
    chip_svg = []
    cx = 40
    for label, val in chips:
        chip_svg.append(f'''
    <text x="{cx}" y="55" font-family="'Fira Code', Consolas, monospace" font-size="28" font-weight="700" fill="{TEXT}">{val}</text>
    <text x="{cx}" y="78" font-family="'Fira Code', Consolas, monospace" font-size="13" fill="{SUBTEXT}">{label}</text>''')
        cx += 180

    # language bar
    bar_x, bar_w = 40, 1080
    segs, legend, x_cursor = [], [], bar_x
    for i, l in enumerate(langs):
        w = round((l["bytes"] / total_bytes) * bar_w, 1)
        color = LANG_COLORS[i % len(LANG_COLORS)]
        segs.append(f'<rect x="{x_cursor}" y="110" width="{w}" height="14" fill="{color}"/>')
        pct = round((l["bytes"] / total_bytes) * 100, 1)
        legend.append((l["name"], pct, color))
        x_cursor += w

    legend_svg, lx, ly = [], 40, 150
    for i, (name, pct, color) in enumerate(legend):
        if i > 0 and i % 3 == 0:
            lx, ly = 40, ly + 24
        legend_svg.append(f'<circle cx="{lx}" cy="{ly - 5}" r="5" fill="{color}"/>')
        legend_svg.append(f'<text x="{lx + 14}" y="{ly}" font-family="\'Fira Code\', Consolas, monospace" font-size="13" fill="{SUBTEXT}">{name} {pct}%</text>')
        lx += 220

    height = 150 + (24 * ((len(legend) - 1) // 3 + 1)) + 20

    svg = f'''<svg width="1160" height="{height}" viewBox="0 0 1160 {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats for {stats['handle']}">
  <rect x="0" y="0" width="1160" height="{height}" rx="14" fill="{BG}"/>
  <text x="40" y="28" font-family="'Fira Code', Consolas, monospace" font-size="13" fill="{SUBTEXT}" opacity="0.7">github.com/{stats['handle']}</text>
  {"".join(chip_svg)}
  {"".join(segs)}
  {"".join(legend_svg)}
  <text x="1120" y="28" text-anchor="end" font-family="'Fira Code', Consolas, monospace" font-size="11" fill="{SUBTEXT}" opacity="0.5">as of {stats['fetched_at']}</text>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
