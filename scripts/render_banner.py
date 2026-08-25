"""
Generates assets/img/banner.svg from data/profile.yml.
Run via `make banner` or as part of `make update`.
"""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "profile.yml"
OUT = ROOT / "assets" / "img" / "banner.svg"

CHAR_W = 13.2          # approx px per monospace char at font-size 22
TYPE_SPEED = 0.06      # seconds per character while typing
DEL_SPEED = 0.045      # seconds per character while deleting
HOLD = 1.0             # seconds to hold each fully-typed word
GAP = 0.4              # seconds between words


def build_svg(profile: dict) -> str:
    name = profile["name"]
    prompt = profile["prompt"]
    words = profile["identities"]

    # Precompute widths and per-word animation ids
    for i, w in enumerate(words):
        w["_width"] = round(len(w["text"]) * CHAR_W)
        w["_type_dur"] = round(len(w["text"]) * TYPE_SPEED, 2)
        w["_del_dur"] = round(len(w["text"]) * DEL_SPEED, 2)
        w["_type_id"] = f"w{i}type"
        w["_del_id"] = f"w{i}del"

    n = len(words)
    clip_defs, text_els, cursor_x_anims = [], [], []

    for i, w in enumerate(words):
        prev_del_id = words[i - 1]["_del_id"] if i > 0 else None
        first_begin = f"0.4s;{words[-1]['_del_id']}.end+{GAP}s" if i == 0 else f"{prev_del_id}.end+{GAP}s"
        del_begin = f"{w['_type_id']}.end+{HOLD}s"

        clip_defs.append(f'''<clipPath id="clip{i}"><rect x="40" y="172" width="0" height="30">
      <animate id="{w['_type_id']}" attributeName="width" from="0" to="{w['_width']}" dur="{w['_type_dur']}s" begin="{first_begin}" fill="freeze"/>
      <animate id="{w['_del_id']}" attributeName="width" from="{w['_width']}" to="0" dur="{w['_del_dur']}s" begin="{del_begin}" fill="freeze"/>
    </rect></clipPath>''')

        text_els.append(
            f'<text x="40" y="196" font-family="\'Fira Code\', Consolas, monospace" '
            f'font-size="22" fill="{w["color"]}" clip-path="url(#clip{i})">{w["text"]}</text>'
        )

        cursor_x_anims.append(f'    <animate attributeName="x" from="40" to="{40 + w["_width"]}" dur="{w["_type_dur"]}s" begin="{first_begin}" fill="freeze"/>')
        cursor_x_anims.append(f'    <animate attributeName="x" from="{40 + w["_width"]}" to="40" dur="{w["_del_dur"]}s" begin="{del_begin}" fill="freeze"/>')

    svg = f'''<svg width="1200" height="260" viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name} banner">
  <title>{name}</title>
  <rect x="0" y="0" width="1200" height="260" rx="18" fill="#181825"/>

  <circle cx="34" cy="30" r="6" fill="#f38ba8"/>
  <circle cx="56" cy="30" r="6" fill="#f9e2af"/>
  <circle cx="78" cy="30" r="6" fill="#a6e3a1"/>
  <line x1="20" y1="50" x2="1180" y2="50" stroke="#a6adc8" stroke-width="1" opacity="0.15"/>

  <text x="40" y="95" font-family="'Fira Code', Consolas, monospace" font-size="18" fill="#89b4fa" opacity="0.85">{prompt}:~$ whoami</text>
  <text x="40" y="145" font-family="'Fira Code', Consolas, monospace" font-size="30" font-weight="700" fill="#cdd6f4">{name}</text>

  <defs>
    {"".join(clip_defs)}
  </defs>

  {"".join(text_els)}

  <rect x="40" y="176" width="3" height="24" fill="#cdd6f4">
    <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>
{chr(10).join(cursor_x_anims)}
  </rect>

  <text x="1160" y="235" text-anchor="end" font-family="'Fira Code', Consolas, monospace" font-size="12" fill="#a6adc8" opacity="0.45">~/{profile["handle"]}</text>
</svg>
'''
    return svg


def main():
    profile = yaml.safe_load(DATA.read_text())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(profile))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
