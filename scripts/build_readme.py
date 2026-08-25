"""
Renders README.md from templates/readme.md.j2 + everything in data/.
This is the last step of `make update` — run after the fetch/render scripts
so the images it references already exist.
"""
import time
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
README = ROOT / "README.md"


def load_yaml(name):
    return yaml.safe_load((DATA / name).read_text())


CHIP_ORDER = ["resume", "linkedin", "codeforces", "atcoder", "cylab", "wca", "instagram", "toph", "email"]


def build_chip_links(profile):
    links = profile.get("links", {})
    out = []
    for key in CHIP_ORDER:
        val = links.get(key)
        if not val:
            continue
        if key == "wca":
            out.append((key, f"https://www.worldcubeassociation.org/persons/{val}"))
        elif key == "email":
            out.append((key, f"mailto:{val}"))
        else:
            out.append((key, val))
    return out


def main():
    achievements = load_yaml("achievements.yml")

    # Derive the CF/CSES highlight from the actual fields instead of hardcoding
    # it as a second copy of the same numbers — this is the one place those
    # numbers get turned into a sentence, so they can't drift out of sync.
    cf = achievements["codeforces"]
    cf_line = f"Codeforces {cf['peak_title']}, peak rating {cf['peak_rating']}, {achievements['cses_solved']} problems solved on CSES"
    achievements["highlights"] = [cf_line] + achievements["highlights"]

    profile = load_yaml("profile.yml")
    context = {
        "profile": profile,
        "achievements": achievements,
        "beyond": load_yaml("beyond.yml"),
        "chip_links": build_chip_links(profile),
        "build_date": time.strftime("%Y-%m-%d"),
    }

    env = Environment(loader=FileSystemLoader(TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("readme.md.j2")
    rendered = template.render(**context)

    README.write_text(rendered)
    print(f"wrote {README}")


if __name__ == "__main__":
    main()
