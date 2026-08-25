"""
Renders one small SVG "chip" per link in profile.yml into assets/img/chips/.
Uses plain text-label chips instead of brand logos — sidesteps the problem of
inconsistent/missing brand icons across services like WCA, Toph, CyLab, and
keeps everything visually uniform with the rest of the self-hosted assets.
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "data" / "profile.yml").read_text())
OUT_DIR = ROOT / "assets" / "img" / "chips"

BG = "#1e1e2e"

# key -> (full label, accent color) — no github chip: the README already lives on GitHub
CHIPS = [
    ("resume",     "Resume",       "#f9e2af"),
    ("linkedin",   "LinkedIn",     "#89b4fa"),
    ("codeforces", "Codeforces",   "#cba6f7"),
    ("atcoder",    "AtCoder",      "#94e2d5"),
    ("cylab",      "CyLab Academy","#a6e3a1"),
    ("wca",        "WCA",          "#f5c2e7"),
    ("instagram",  "Instagram",    "#f38ba8"),
    ("toph",       "Toph",         "#74c7ec"),
    ("email",      "Email",        "#f9e2af"),
]

# chip geometry — smaller font, wider & shorter card than the old 40px-tall version
HEIGHT = 28
FONT_SIZE = 11
CHAR_W = 6.7   # approx px per char at font-size 11 in Fira Code
PAD_X = 14


def chip_svg(label, color):
    width = round(PAD_X * 2 + len(label) * CHAR_W)
    return f'''<svg width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{HEIGHT - 1.5}" rx="7" fill="{BG}" stroke="{color}" stroke-opacity="0.45" stroke-width="1.1"/>
  <text x="{width / 2}" y="{HEIGHT / 2 + 3.8}" text-anchor="middle" font-family="'Fira Code', Consolas, monospace" font-size="{FONT_SIZE}" font-weight="600" fill="{color}">{label}</text>
</svg>
'''


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    links = PROFILE.get("links", {})
    written = []
    for key, label, color in CHIPS:
        if links.get(key) is None:
            continue  # skip chips whose data isn't filled in yet
        path = OUT_DIR / f"{key}.svg"
        path.write_text(chip_svg(label, color))
        written.append(key)
    print(f"wrote {len(written)} chips: {', '.join(written)}")


if __name__ == "__main__":
    main()
