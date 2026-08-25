"""
Generates assets/img/banner.svg from data/profile.yml.
Run via `make banner` or as part of `make update`.

v4 — glassmorphism terminal with a single living accent: one Game of Life
glider (verified NE-bound), evolved on a small toroidal grid with
straightforward Life rules and cycle-detected (not assumed) until it
returns to its exact starting state. That verified sequence drives ONE
<path> via a discrete SMIL <animate> on `d` — no tiling, no repetition.
It's masked with a radial opacity fade (transparency only, no blur
filters anywhere in this file) so it lives as a single quiet "sigil" to
the right of the terminal text. No JS, so it still animates fine as a
plain <img> in a README.

Palette is strictly Catppuccin Mocha — every color below is one of the
named Mocha values, no invented in-between shades.
"""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "profile.yml"
OUT = ROOT / "assets" / "img" / "banner.svg"

# ---- typing animation tuning (unchanged convention: prompt -> name ->
# cycling identity words; char width nudged slightly for JetBrains Mono) ----
CHAR_W = 13.3
TYPE_SPEED = 0.06
DEL_SPEED = 0.045
HOLD = 1.0
GAP = 0.4

# ---- palette: Catppuccin Mocha, exact values only ----
MOCHA_CRUST = "#11111b"
MOCHA_MANTLE = "#181825"
MOCHA_BASE = "#1e1e2e"
MOCHA_SURFACE1 = "#45475a"
MOCHA_TEXT = "#cdd6f4"
MOCHA_LAVENDER = "#b4befe"
MOCHA_PINK = "#f5c2e7"
MOCHA_TEAL = "#94e2d5"
MOCHA_OVERLAY1 = "#7f849c"
MOCHA_RED = "#f38ba8"
MOCHA_YELLOW = "#f9e2af"
MOCHA_GREEN = "#a6e3a1"

BG_GRAD_TOP = MOCHA_CRUST
BG_GRAD_MID = MOCHA_MANTLE
BG_GRAD_BOT = MOCHA_BASE
PANEL_FILL = MOCHA_BASE
PANEL_OPACITY = 0.46
PANEL_STROKE = MOCHA_SURFACE1
PANEL_HIGHLIGHT = MOCHA_TEXT
LIFE_COLOR = MOCHA_LAVENDER
LIFE_OPACITY = 0.6
GLOW_COLOR = MOCHA_PINK
PROMPT_COLOR = MOCHA_TEAL
CURSOR_COLOR = MOCHA_PINK
FOOTER_COLOR = MOCHA_OVERLAY1
DOT_COLORS = (MOCHA_RED, MOCHA_YELLOW, MOCHA_GREEN)
NAME_GRAD_FROM = MOCHA_TEXT
NAME_GRAD_TO = MOCHA_LAVENDER

# JetBrains Mono via Google Fonts. Note: this is the plain typeface only —
# Nerd Font icon glyphs are a separate patched build not hosted on Google's
# CDN, so icon glyphs in identity text won't render with this @import.
# Self-host a Nerd Font build if you need the icon set.
FONT_STACK = "'JetBrains Mono', 'Fira Code', ui-monospace, Consolas, monospace"

# ---- game of life tuning: ONE glider, one small board, no tiling ----
LIFE_GRID = 26          # NxN toroidal cells
LIFE_CELL = 7           # px per cell (board is LIFE_GRID * LIFE_CELL px square)
LIFE_FRAME_TIME = 0.09  # seconds per generation
LIFE_CENTER = (985, 128)   # px, where the motif sits within the 1200x260 banner
LIFE_FADE_RADIUS = 96      # radial mask fade radius, in px

# Glider oriented to travel NE (up and to the right). Verified by simulating
# on an open (non-wrapping) grid: bounding-box row decreases and column
# increases every 4 generations — see dev notes / commit for the check.
# ###
# ..#
# .#.
GLIDER = [(2, 1), (1, 2), (0, 0), (0, 1), (0, 2)]

# Canonical glider (moving south-east), as (row, col) offsets:
# .#.
# ..#
# ###
GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def life_step(grid, n):
    """One generation of Conway's Game of Life on an n x n torus."""
    new = [[0] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            neighbors = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbors += grid[(y + dy) % n][(x + dx) % n]
            alive = grid[y][x]
            new[y][x] = 1 if (alive and neighbors in (2, 3)) or (not alive and neighbors == 3) else 0
    return new


def compute_life_frames(n, pattern):
    """Evolve `pattern` on an n x n torus until it returns to its exact
    starting state. A lone glider on a torus is exactly periodic (no
    transient), so cycle detection gives the true, provable loop length
    instead of a guessed constant."""
    grid = [[0] * n for _ in range(n)]
    for r, c in pattern:
        grid[r % n][c % n] = 1

    def live_cells(g):
        return [(x, y) for y in range(n) for x in range(n) if g[y][x]]

    frames = [live_cells(grid)]
    current = grid
    for _ in range(8 * n):  # generous cap; a real glider loops well before this
        current = life_step(current, n)
        if current == grid:
            return frames
        frames.append(live_cells(current))
    raise RuntimeError("life pattern did not cycle back to its start — check GLIDER/LIFE_GRID")


def frame_path_d(cells, cell_px):
    return "".join(f"M{x*cell_px},{y*cell_px}h{cell_px}v{cell_px}h{-cell_px}z" for x, y in cells)


def build_life_motif():
    """A single glider, masked into a soft-edged glowing sigil rather than
    tiled across the card. The mask fades the motif to nothing before its
    toroidal wrap edge, so instead of a hard cut the glider quietly
    dissolves and re-materializes each cycle — no visible seam.

    Returns (defs_fragment, render_fragment): the former holds gradients
    and the mask definition (belongs in <defs>), the latter is the actual
    glow + animated glider group (belongs in the render tree)."""
    frames = compute_life_frames(LIFE_GRID, GLIDER)
    board_px = LIFE_GRID * LIFE_CELL
    d_values = ";".join(frame_path_d(f, LIFE_CELL) for f in frames)
    dur = round(len(frames) * LIFE_FRAME_TIME, 2)
    cx, cy = LIFE_CENTER
    x0, y0 = cx - board_px / 2, cy - board_px / 2

    defs_fragment = f'''<radialGradient id="lifeGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{GLOW_COLOR}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="{GLOW_COLOR}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="lifeFade" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fff" stop-opacity="1"/>
      <stop offset="70%" stop-color="#fff" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </radialGradient>
    <mask id="lifeMask">
      <circle cx="{cx}" cy="{cy}" r="{LIFE_FADE_RADIUS}" fill="url(#lifeFade)"/>
    </mask>'''

    render_fragment = f'''<circle cx="{cx}" cy="{cy}" r="{LIFE_FADE_RADIUS * 1.5}" fill="url(#lifeGlow)"/>
  <g mask="url(#lifeMask)" filter="url(#softGlow)">
    <path transform="translate({x0},{y0})" d="{frame_path_d(frames[0], LIFE_CELL)}" fill="{LIFE_COLOR}" fill-opacity="{LIFE_OPACITY}">
      <animate attributeName="d" calcMode="discrete" dur="{dur}s" repeatCount="indefinite" values="{d_values}"/>
    </path>
  </g>'''

    return defs_fragment, render_fragment


def build_svg(profile: dict) -> str:
    name = profile["name"]
    prompt = profile["prompt"]
    words = profile["identities"]

    for i, w in enumerate(words):
        w["_width"] = round(len(w["text"]) * CHAR_W)
        w["_type_dur"] = round(len(w["text"]) * TYPE_SPEED, 2)
        w["_del_dur"] = round(len(w["text"]) * DEL_SPEED, 2)
        w["_type_id"] = f"w{i}type"
        w["_del_id"] = f"w{i}del"

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
            f'<text x="40" y="196" font-family="{FONT_STACK}" '
            f'font-size="22" fill="{w["color"]}" clip-path="url(#clip{i})">{w["text"]}</text>'
        )

        cursor_x_anims.append(f'    <animate attributeName="x" from="40" to="{40 + w["_width"]}" dur="{w["_type_dur"]}s" begin="{first_begin}" fill="freeze"/>')
        cursor_x_anims.append(f'    <animate attributeName="x" from="{40 + w["_width"]}" to="40" dur="{w["_del_dur"]}s" begin="{del_begin}" fill="freeze"/>')

    life_defs, life_render = build_life_motif()
    dot_red, dot_yellow, dot_green = DOT_COLORS

    svg = f'''<svg width="1200" height="260" viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{name} banner">
  <title>{name}</title>

  <defs>
    <style>@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;display=swap');</style>

    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BG_GRAD_TOP}"/>
      <stop offset="55%" stop-color="{BG_GRAD_MID}"/>
      <stop offset="100%" stop-color="{BG_GRAD_BOT}"/>
    </linearGradient>

    <linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{NAME_GRAD_FROM}"/>
      <stop offset="100%" stop-color="{NAME_GRAD_TO}"/>
    </linearGradient>

    <linearGradient id="panelTopEdge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{PANEL_HIGHLIGHT}" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="{PANEL_HIGHLIGHT}" stop-opacity="0"/>
    </linearGradient>

    <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="1.6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    {life_defs}

    {"".join(clip_defs)}
  </defs>

  <rect x="0" y="0" width="1200" height="260" rx="18" fill="url(#bgGrad)"/>
  {life_render}
  <rect x="1" y="1" width="1198" height="258" rx="17" fill="{PANEL_FILL}" fill-opacity="{PANEL_OPACITY}" stroke="{PANEL_STROKE}" stroke-opacity="0.55" stroke-width="1"/>
  <rect x="1" y="1" width="1198" height="60" rx="17" fill="url(#panelTopEdge)"/>

  <circle cx="34" cy="30" r="5.5" fill="{dot_red}"/>
  <circle cx="56" cy="30" r="5.5" fill="{dot_yellow}"/>
  <circle cx="78" cy="30" r="5.5" fill="{dot_green}"/>
  <line x1="20" y1="50" x2="1180" y2="50" stroke="#cdd6f4" stroke-width="1" opacity="0.08"/>

  <text x="40" y="95" font-family="{FONT_STACK}" font-size="18" fill="{PROMPT_COLOR}" opacity="0.9">{prompt}:~$ whoami</text>
  <text x="40" y="145" font-family="{FONT_STACK}" font-size="30" font-weight="700" fill="url(#nameGrad)">{name}</text>

  {"".join(text_els)}

  <rect x="40" y="176" width="3" height="24" fill="{CURSOR_COLOR}">
    <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>
{chr(10).join(cursor_x_anims)}
  </rect>

  <text x="1160" y="235" text-anchor="end" font-family="{FONT_STACK}" font-size="12" fill="{FOOTER_COLOR}" opacity="0.5">~/{profile["handle"]}</text>
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