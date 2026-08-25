"""
Renders assets/img/tech_stack.svg — a row of plain monospace pills, one per
entry in data/beyond.yml's tech_stack list. Replaces skillicons.dev: no
external service, and the flat text-pill look matches the rest of the
self-hosted assets better than colorful cartoon icons.
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
BEYOND = yaml.safe_load((ROOT / "data" / "beyond.yml").read_text())
OUT = ROOT / "assets" / "img" / "tech_stack.svg"

BG, BORDER, TEXT = "#181825", "#45475a", "#cdd6f4"

DISPLAY_NAMES = {
    "cpp": "C++", "python": "Python", "java": "Java", "rust": "Rust",
    "linux": "Linux", "git": "Git", "react": "React", "spring": "Spring",
    "javascript": "JavaScript", "typescript": "TypeScript",
}


def main():
    items = [DISPLAY_NAMES.get(t, t.capitalize()) for t in BEYOND["tech_stack"]]

    pills, x, pad, gap, h = [], 12, 16, 10, 34
    for label in items:
        w = pad * 2 + len(label) * 9
        pills.append(f'''<rect x="{x}" y="0" width="{w}" height="{h}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text x="{x + w / 2}" y="22" text-anchor="middle" font-family="'Fira Code', Consolas, monospace" font-size="13" fill="{TEXT}">{label}</text>''')
        x += w + gap

    total_w = x - gap + 12
    svg = f'''<svg width="{total_w}" height="{h}" viewBox="0 0 {total_w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Tech stack">
{"".join(pills)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
