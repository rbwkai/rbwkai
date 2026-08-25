"""
Renders one small SVG "chip" per link in profile.yml into assets/img/chips/.
Uses plain monogram labels instead of brand logos — sidesteps the problem of
inconsistent/missing brand icons across services like WCA, Toph, picoCTF, and
keeps everything visually uniform with the rest of the self-hosted assets.
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "data" / "profile.yml").read_text())
OUT_DIR = ROOT / "assets" / "img" / "chips"

BG = "#1e1e2e"

# key -> (monogram label, accent color, condition on profile.links)
CHIPS = [
    ("github",     "GH",   "#b4befe"),
    ("linkedin",   "LI",   "#89b4fa"),
    ("codeforces", "CF",   "#cba6f7"),
    ("atcoder",    "AC",   "#94e2d5"),
    ("picoctf",    "PC",   "#a6e3a1"),
    ("wca",        "WCA",  "#f5c2e7"),
    ("instagram",  "IG",   "#f38ba8"),
    ("toph",       "TOPH", "#74c7ec"),
    ("email",      "MAIL", "#f9e2af"),
]


def chip_svg(label, color):
    width = 26 + len(label) * 12
    return f'''<svg width="{width}" height="40" viewBox="0 0 {width} 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="38.5" rx="9" fill="{BG}" stroke="{color}" stroke-opacity="0.45" stroke-width="1.2"/>
  <text x="{width / 2}" y="25" text-anchor="middle" font-family="'Fira Code', Consolas, monospace" font-size="14" font-weight="700" fill="{color}">{label}</text>
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
