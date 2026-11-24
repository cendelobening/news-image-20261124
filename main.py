#!/usr/bin/env python3
"""THE WORLD TODAY - a one-page newspaper front page, drawn pixel by pixel.

Pure standard library. A small grayscale canvas, a hand-cut 5x7 bitmap
typeface, and a home-grown PNG writer (zlib + struct) render the front
page of Tuesday 24 November 2026 to entry.png at 1024x1024.
"""

import os
import struct
import zlib

SIDE = 1024
PAPER = 246          # newsprint off-white
INK = 26             # near-black ink
FADE = 118           # grey for rules and captions
OUTPUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

# ---------------------------------------------------------------------------
# Typeface. Each glyph is seven rows of five pixels, rows joined with '/'.
# ---------------------------------------------------------------------------

def _g(rows):
    return tuple(rows.split("/"))

FONT = {
    "A": _g(".###./#...#/#...#/#####/#...#/#...#/#...#"),
    "B": _g("####./#...#/#...#/####./#...#/#...#/####."),
    "C": _g(".####/#..../#..../#..../#..../#..../.####"),
    "D": _g("####./#...#/#...#/#...#/#...#/#...#/####."),
    "E": _g("#####/#..../#..../####./#..../#..../#####"),
    "F": _g("#####/#..../#..../####./#..../#..../#...."),
    "G": _g(".####/#..../#..../#.###/#...#/#...#/.###."),
    "H": _g("#...#/#...#/#...#/#####/#...#/#...#/#...#"),
    "I": _g("#####/..#../..#../..#../..#../..#../#####"),
    "J": _g("..###/...#./...#./...#./...#./#..#./.##.."),
    "K": _g("#...#/#..#./#.#../##.../#.#../#..#./#...#"),
    "L": _g("#..../#..../#..../#..../#..../#..../#####"),
    "M": _g("#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#"),
    "N": _g("#...#/##..#/#.#.#/#..##/#...#/#...#/#...#"),
    "O": _g(".###./#...#/#...#/#...#/#...#/#...#/.###."),
    "P": _g("####./#...#/#...#/####./#..../#..../#...."),
    "Q": _g(".###./#...#/#...#/#...#/#.#.#/#..#./.##.#"),
    "R": _g("####./#...#/#...#/####./#.#../#..#./#...#"),
    "S": _g(".####/#..../#..../.###./....#/....#/####."),
    "T": _g("#####/..#../..#../..#../..#../..#../..#.."),
    "U": _g("#...#/#...#/#...#/#...#/#...#/#...#/.###."),
    "V": _g("#...#/#...#/#...#/#...#/#...#/.#.#./..#.."),
    "W": _g("#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#"),
    "X": _g("#...#/.#.#./..#../..#../.#.#./#...#/#...#"),
    "Y": _g("#...#/#...#/.#.#./..#../..#../..#../..#.."),
    "Z": _g("#####/....#/..##./..#../.#.../#..../#####"),
    "a": _g("...../...../.###./....#/.####/#...#/.####"),
    "b": _g("#..../#..../####./#...#/#...#/#...#/####."),
    "c": _g("...../...../.####/#..../#..../#..../.####"),
    "d": _g("....#/....#/.####/#...#/#...#/#...#/.####"),
    "e": _g("...../...../.###./#...#/#####/#..../.###."),
    "f": _g("..##./.#.../####./.#.../.#.../.#.../.#..."),
    "g": _g("...../...../.####/#...#/#...#/.####/..##."),
    "h": _g("#..../#..../####./#...#/#...#/#...#/#...#"),
    "i": _g("..#../...../.##../..#../..#../..#../.###."),
    "j": _g("...#./...../..##./...#./...#./...#./.##.."),
    "k": _g("#..../#..../#..#./#.#../##.../#.#../#..#."),
    "l": _g(".##../..#../..#../..#../..#../..#../.###."),
    "m": _g("...../...../##.#./#.#.#/#.#.#/#.#.#/#.#.#"),
    "n": _g("...../...../####./#...#/#...#/#...#/#...#"),
    "o": _g("...../...../.###./#...#/#...#/#...#/.###."),
    "p": _g("...../...../####./#...#/#...#/####./#...."),
    "q": _g("...../...../.####/#...#/#...#/.####/....#"),
    "r": _g("...../...../#.##./##..#/#..../#..../#...."),
    "s": _g("...../...../.####/#..../.###./....#/####."),
    "t": _g(".#.../.#.../####./.#.../.#.../.#..#/..##."),
    "u": _g("...../...../#...#/#...#/#...#/#..##/.##.#"),
    "v": _g("...../...../#...#/#...#/#...#/.#.#./..#.."),
    "w": _g("...../...../#...#/#.#.#/#.#.#/#.#.#/.#.#."),
    "x": _g("...../...../#...#/.#.#./..#../.#.#./#...#"),
    "y": _g("...../...../#...#/#...#/#...#/.####/....#"),
    "z": _g("...../...../#####/...#./..#../.#.../#####"),
    "0": _g(".###./#...#/#..##/#.#.#/##..#/#...#/.###."),
    "1": _g("..#../.##../..#../..#../..#../..#../.###."),
    "2": _g(".###./#...#/....#/..##./.#.../#..../#####"),
    "3": _g("####./....#/....#/.###./....#/....#/####."),
    "4": _g("...#./..##./.#.#./#..#./#####/...#./...#."),
    "5": _g("#####/#..../####./....#/....#/#...#/.###."),
    "6": _g(".###./#..../#..../####./#...#/#...#/.###."),
    "7": _g("#####/....#/..##./..#../..#../..#../..#.."),
    "8": _g(".###./#...#/#...#/.###./#...#/#...#/.###."),
    "9": _g(".###./#...#/#...#/.####/....#/....#/.###."),
    " ": _g("...../...../...../...../...../...../....."),
    ".": _g("...../...../...../...../...../.##../.##.."),
    ",": _g("...../...../...../...../.##../.##../.#..."),
    "'": _g("..#../..#../.#.../...../...../...../....."),
    '"': _g(".#.#./.#.#./...../...../...../...../....."),
    ":": _g("...../.##../.##../...../.##../.##../....."),
    ";": _g("...../.##../.##../...../.##../.##../.#..."),
    "-": _g("...../...../...../#####/...../...../....."),
    "(": _g("...##/..#../.#.../.#.../.#.../..#../...##"),
    ")": _g("##.../..#../...#./...#./...#./..#../##..."),
    "/": _g("....#/....#/..##./..#../.#.../#..../#...."),
    "&": _g(".##../#..#./#.#../.#.../#.#.#/#..#./.##.#"),
    "%": _g("##..#/##.#./....#/..#../.#.../#..../#..##"),
    "$": _g("..#../.####/#.#../.###./..#.#/####./..#.."),
    "+": _g("...../..#../..#../#####/..#../..#../....."),
    "!": _g("..#../..#../..#../..#../..#../...../..#.."),
    "?": _g(".###./#...#/....#/..##./..#../...../..#.."),
    "|": _g("..#../..#../..#../..#../..#../..#../..#.."),
}

CELL_W = 6   # glyph cell advance, in font units
CELL_H = 8   # glyph cell line step, in font units


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

class Sheet:
    """A square grayscale page you can ink rectangles and letters onto."""

    def __init__(self, side=SIDE, tone=PAPER):
        self.side = side
        self.px = bytearray([tone]) * (side * side)

    def dot(self, x, y, tone):
        if 0 <= x < self.side and 0 <= y < self.side:
            self.px[y * self.side + x] = tone

    def block(self, x, y, w, h, tone):
        for yy in range(y, y + h):
            if 0 <= yy < self.side:
                base = yy * self.side
                for xx in range(x, x + w):
                    if 0 <= xx < self.side:
                        self.px[base + xx] = tone

    def rule_h(self, x, y, w, tone=INK, thick=2):
        self.block(x, y, w, thick, tone)

    def rule_v(self, x, y, h, tone=INK, thick=2):
        self.block(x, y, thick, h, tone)

    def frame(self, x, y, w, h, tone=INK, thick=2):
        self.rule_h(x, y, w, tone, thick)
        self.rule_h(x, y + h - thick, w, tone, thick)
        self.rule_v(x, y, h, tone, thick)
        self.rule_v(x + w - thick, y, h, tone, thick)

    def letter(self, ch, x, y, scale, tone=INK):
        glyph = FONT.get(ch, FONT["?"])
        for r, row in enumerate(glyph):
            for c, mark in enumerate(row):
                if mark == "#":
                    self.block(x + c * scale, y + r * scale, scale, scale, tone)

    def text(self, s, x, y, scale, tone=INK):
        cx = x
        for ch in s:
            self.letter(ch, cx, y, scale, tone)
            cx += CELL_W * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * CELL_W * scale

    def centered(self, s, y, scale, tone=INK, cx=None):
        middle = self.side // 2 if cx is None else cx
        self.text(s, middle - self.text_width(s, scale) // 2, y, scale, tone)


# ---------------------------------------------------------------------------
# Text flow helpers
# ---------------------------------------------------------------------------

def wrap_words(words, width_px, scale):
    """Greedy word wrap: returns a list of line strings fitting width_px."""
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) * CELL_W * scale <= width_px:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def flow_text(sheet, text_body, x, y, width, scale=2, step=16, tone=INK):
    """Set a single column of body copy; returns the y just past the text."""
    lines = wrap_words(text_body.split(), width, scale)
    for j, line in enumerate(lines):
        sheet.text(line, x, y + j * step, scale, tone)
    return y + len(lines) * step


def two_columns(sheet, text_body, x, y, total_w, scale=2, step=16, gap=26):
    """Split body copy across two balanced columns; returns bottom y."""
    col_w = (total_w - gap) // 2
    lines = wrap_words(text_body.split(), col_w, scale)
    half = (len(lines) + 1) // 2
    for i, part in enumerate((lines[:half], lines[half:])):
        for j, line in enumerate(part):
            sheet.text(line, x + i * (col_w + gap), y + j * step, scale)
    return y + half * step


def headline_block(sheet, lines, x, y, scale, step):
    for i, line in enumerate(lines):
        sheet.text(line, x, y + i * step, scale)
    return y + len(lines) * step


# ---------------------------------------------------------------------------
# Picture: a little halftone skyline for the lead story (deterministic).
# ---------------------------------------------------------------------------

def skyline(sheet, x, y, w, h):
    sheet.frame(x, y, w, h, INK, 3)
    base = y + h - 24
    for yy in range(y + 10, base - 40, 14):
        for xx in range(x + 10, x + w - 10, 14):
            if (xx * 7 + yy * 13) % 5 == 0:
                sheet.block(xx, yy, 3, 3, FADE)
    heights = [64, 96, 78, 112, 70, 104, 86, 58, 108, 80, 66, 92]
    tw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + 6 + i * tw
        sheet.block(bx, base - hh, tw - 8, hh, INK)
        for wy in range(base - hh + 9, base - 10, 15):
            for wx in range(bx + 5, bx + tw - 13, 11):
                if (wx + wy) % 3:
                    sheet.block(wx, wy, 4, 5, PAPER)
    sheet.block(x + 3, base, w - 6, 3, INK)
    sheet.centered("STOCKHOLM - THE SUMMIT CITY", base + 7, 1, FADE,
                   cx=x + w // 2)


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------

LEAD_HEAD = ["EUROPE RALLIES BEHIND UKRAINE", "AS PEACE PLAN SPARKS ALARM"]
LEAD_BODY = (
    "Leaders from across Europe gathered in Stockholm for the fourth "
    "Crimea Platform summit and closed ranks behind Kyiv. A 28-point "
    "peace plan backed by Donald Trump has alarmed allies who fear it "
    "rewards land seized by force. President Zelensky said Ukraine "
    "would never accept a settlement that hands territory to the "
    "aggressor, and capitals promised fresh support."
)

GRID = [
    ("AMERICAS",
     ["US BRANDS CARTEL DE LOS", "SOLES A TERROR GROUP"],
     "Washington has named Venezuela's Cartel de los Soles a "
     "terrorist group as a US carrier patrols the Caribbean. US "
     "strikes on boats since September total 21, with 83 killed."),
    ("BRITAIN",
     ["12,000 EVACUATED FROM", "MANCHESTER CONCERT"],
     "A concert in Manchester was evacuated after an unknown "
     "substance was released inside the venue. Around 12,000 fans "
     "were led out while crews checked the air for danger."),
    ("BALTIC",
     ["RUSSIAN CARGO SHIP BURNS", "OFF THE FINNISH COAST"],
     "A Russian cargo ship caught fire off the Finnish coast after "
     "a reported drone hit. Finnish crews fought the blaze while "
     "Moscow moved to haul the stricken vessel away."),
    ("INDIA - NEPAL",
     ["FIRST AYODHYA-JANAKPUR", "TRAIN IS FLAGGED OFF"],
     "Prime Minister Modi and Home Minister Shah flagged off the "
     "first Ayodhya to Janakpur train, the Saryu-Kamala Express, "
     "a new rail link between India and Nepal."),
    ("IRAN",
     ["SINGER SENTENCED TO 74", "LASHES OVER CONCERT"],
     "Iranian singer Parastoo Ahmadi has been sentenced to 74 "
     "lashes over a virtual concert performed without a hijab, "
     "drawing condemnation from rights groups worldwide."),
]

STRIP = [
    "BOLSONARO BACK IN JAIL IN BRAZIL",
    "FERRARI UNVEILS 296 TWINS IN SPAIN",
    "NVIDIA SOARS AS HUANG RETURNS AS CEO",
]


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def compose():
    pg = Sheet()
    m = 46                      # page margin
    inner = SIDE - 2 * m        # usable width

    # Masthead
    pg.rule_h(m, 30, inner, INK, 5)
    pg.centered("THE WORLD TODAY", 46, 9)
    pg.rule_h(m, 46 + 8 * 9 + 8, inner, INK, 2)
    dline = 140
    pg.text("TUESDAY 24 NOVEMBER 2026", m, dline, 2)
    right = "ONE PAGE - ALL THE NEWS"
    pg.text(right, SIDE - m - pg.text_width(right, 2), dline, 2, FADE)
    pg.rule_h(m, 166, inner, INK, 4)

    # Lead headline, full width
    hy = headline_block(pg, LEAD_HEAD, m, 182, 5, 48)
    pg.text("STOCKHOLM / KYIV -", m, hy + 4, 2, FADE)

    # Lead row: picture left, two body columns right
    top = hy + 30
    skyline(pg, m, top, 300, 150)
    bx = m + 326
    two_columns(pg, LEAD_BODY, bx, top + 2, SIDE - m - bx)

    # Stat boxes
    sy = top + 168
    stats = [("28", "POINTS IN THE PLAN"), ("4TH", "CRIMEA PLATFORM SUMMIT"),
             ("STOCKHOLM", "HOST CITY, SWEDEN")]
    bw = (inner - 2 * 22) // 3
    for i, (big, small) in enumerate(stats):
        x0 = m + i * (bw + 22)
        pg.frame(x0, sy, bw, 56)
        pg.centered(big, sy + 8, 3, INK, cx=x0 + bw // 2)
        pg.centered(small, sy + 38, 1, FADE, cx=x0 + bw // 2)
    pg.rule_h(m, sy + 70, inner, INK, 3)

    # Grid of five stories: three over two
    gy = sy + 92
    colw = (inner - 2 * 24) // 3
    rowh = 186
    spots = [(m, gy), (m + colw + 24, gy), (m + 2 * (colw + 24), gy),
             (m, gy + rowh), (m + colw + 24, gy + rowh)]
    for idx, (gx, yy) in enumerate(spots):
        kicker, heads, body = GRID[idx]
        pg.text(kicker, gx, yy, 2, FADE)
        hyy = headline_block(pg, heads, gx, yy + 20, 2, 19)
        flow_text(pg, body, gx, hyy + 4, colw, step=15)
    for sx in (m + colw + 11, m + 2 * colw + 35):
        pg.rule_v(sx, gy, rowh - 8, FADE, 1)
        pg.rule_v(sx, gy + rowh, rowh - 8, FADE, 1)

    # Bottom strip
    by = gy + 2 * rowh + 12
    pg.rule_h(m, by, inner, INK, 4)
    sw = inner // 3
    for i, item in enumerate(STRIP):
        for j, line in enumerate(wrap_words(item.split(), sw - 28, 2)):
            pg.centered(line, by + 12 + j * 18, 2, INK, cx=m + i * sw + sw // 2)
        if i:
            pg.rule_v(m + i * sw, by + 8, 40, FADE, 1)
    pg.rule_h(m, by + 54, inner, INK, 2)
    pg.centered("THE WORLD TODAY - PRINTED BY MACHINE, READ BY HUMANS",
                by + 62, 1, FADE)
    return pg


# ---------------------------------------------------------------------------
# PNG writer (grayscale, filter 0 rows, fixed compression -> deterministic)
# ---------------------------------------------------------------------------

def _chunk(tag, payload):
    return (struct.pack(">I", len(payload)) + tag + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))


def save_png(sheet, path):
    raw = bytearray()
    stride = sheet.side
    for yy in range(sheet.side):
        raw.append(0)
        raw.extend(sheet.px[yy * stride:(yy + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", sheet.side, sheet.side, 8, 0, 0, 0, 0)
    blob = (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(blob)
    os.chmod(path, 0o644)


def main():
    page = compose()
    save_png(page, OUTPUT)
    print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
