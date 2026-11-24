#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Tuesday 24 November 2026.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the
day's world news, using only the Python standard library.  The bitmap
font, the PNG encoder and every picture on the page are built by hand
in this file; the program reads no input files and uses no network.
Deterministic: two runs write byte-identical files.

The day's stories (24 November 2026): European leaders rally behind
Ukraine at the Crimea Platform summit in Stockholm as Trump's
28-point peace plan sparks alarm; Washington brands Venezuela's
Cartel de los Soles a terrorist organisation; 12,000 fans are
evacuated from a Manchester concert in a gas scare; Modi and Shah
flag off the first Ayodhya-Janakpur train; an Iranian singer is
sentenced to 74 lashes over a virtual concert; a Russian cargo ship
burns off Finland after a reported drone hit.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 241, 227)
INK = (34, 30, 28)
BURG = (122, 31, 43)
BURG_DARK = (88, 19, 30)
GOLD = (198, 160, 40)
CREAM = (247, 241, 227)
FOREST = (44, 90, 60)
RUST = (176, 84, 32)
ORANGE = (196, 90, 24)
PLUM = (104, 58, 96)
SLATE = (52, 78, 110)
SKY = (178, 216, 236)
SAND = (226, 202, 152)
WHITE = (255, 255, 255)
GREY = (120, 120, 122)
DARK = (52, 52, 56)
GREEN = (46, 125, 62)
BLUE = (52, 110, 170)
RED = (178, 44, 36)
YELLOW = (232, 196, 64)
UKR_BLUE = (38, 96, 176)
UKR_YELLOW = (245, 205, 40)
SEA = (64, 116, 158)

# ------------------------------------------------------------ bitmap font
# Hand-built 5x7 glyphs: each glyph is 7 rows, each row a 5-bit number.
# Bit 4 is the leftmost pixel of the row.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    ":": (0, 0x0C, 0, 0, 0, 0x0C, 0),
    ";": (0, 0x0C, 0, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "\u2022": (0, 0, 0x0C, 0x0C, 0, 0, 0),
}
BLANK = (0, 0, 0, 0, 0, 0, 0)


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (1px gaps)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            rad = max(1, thick // 2)
            self.circle(x, y, rad, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.polygon([(x0, y0), (x1, y1), (x2, y2)], color)

    def polygon(self, pts, color):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if ay == by:
                    continue
                if (ay <= y < by) or (by <= y < ay):
                    x = ax + (y - ay) * (bx - ax) // (by - ay)
                    xs.append(x)
            if len(xs) >= 2:
                xs.sort()
                self.rect(xs[0], y, xs[-1] - xs[0] + 1, 1, color)

    # ------------------------------------------------------------- text
    def char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color, align="left"):
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            self.char(cx, y, ch, scale, color)
            cx += 6 * scale
        return w


# ------------------------------------------------------------------ PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# -------------------------------------------------------------- pictograms
def stockholm_scene(cv, x, y, w, h):
    """Stockholm waterfront: spires, the Ukrainian and EU flags, a dove."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + 52, y + 40, 24, GOLD)              # low northern sun
    # dove of peace over the water
    dx, dy = x + w - 118, y + 34
    cv.polygon([(dx, dy), (dx + 34, dy - 10), (dx + 26, dy + 4),
                (dx + 44, dy + 8), (dx + 20, dy + 12), (dx + 6, dy + 8)],
               WHITE)
    cv.line(dx + 30, dy + 10, dx + 44, dy + 18, GREEN, 2)   # olive twig
    # skyline: town hall tower, church spire, domes
    base = y + h - 84
    cv.rect(x, base, w, 4, INK)
    cv.rect(x + 26, base - 64, 52, 64, (150, 96, 70))        # town hall block
    cv.rect(x + 44, base - 108, 16, 44, (150, 96, 70))       # its tower
    cv.triangle(x + 40, base - 108, x + 64, base - 108,
                x + 52, base - 132, (60, 60, 64))
    cv.rect(x + 96, base - 44, 60, 44, (168, 128, 92))
    cv.triangle(x + 92, base - 44, x + 160, base - 44,
                x + 126, base - 96, FOREST)                  # church spire
    cv.rect(x + 176, base - 40, 64, 40, (158, 112, 82))
    cv.circle(x + 208, base - 40, 22, (96, 120, 108))        # dome
    cv.rect(x + 258, base - 52, 44, 52, (150, 96, 70))
    cv.triangle(x + 254, base - 52, x + 306, base - 52,
                x + 280, base - 84, (60, 60, 64))
    for bx in range(x + 18, x + w - 18, 34):                 # windows
        cv.rect(bx, base - 26, 8, 10, GOLD)
    # harbour water
    cv.rect(x, base + 4, w, h - (base + 4 - y), SEA)
    for wy in (base + 22, base + 44, base + 64):
        for wx in range(x + 12, x + w - 24, 44):
            cv.rect(wx, wy, 22, 3, WHITE)
    # flags on poles at the quay
    cv.vline(x + 30, y + 84, 96, INK)
    cv.rect(x + 30, y + 84, 52, 14, UKR_BLUE)                # Ukraine: blue
    cv.rect(x + 30, y + 98, 52, 14, UKR_YELLOW)              # over yellow
    cv.vline(x + w - 30, y + 84, 96, INK)
    cv.rect(x + w - 82, y + 84, 52, 28, UKR_BLUE)            # EU flag
    for sx, sy in ((10, 5), (24, 2), (38, 5), (42, 14),
                   (38, 23), (24, 26), (10, 23), (6, 14)):
        cv.rect(x + w - 82 + sx, y + 84 + sy, 3, 3, GOLD)    # star circle
    # caption strip
    cv.rect(x, y + h - 28, w, 28, INK)
    cv.text(x + w // 2, y + h - 21, "CRIMEA PLATFORM SUMMIT, STOCKHOLM",
            1, CREAM, align="center")


def carrier_strip(cv, x, y, w, h):
    """An aircraft carrier in the Caribbean, a jet lifting off."""
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y, w, 14, SKY)
    cv.circle(x + 36, y + 7, 6, GOLD)
    # carrier: long flat deck, island tower, hull below the waterline
    cv.rect(x + 60, y + 26, 330, 7, DARK)
    cv.rect(x + 268, y + 14, 30, 12, DARK)
    cv.rect(x + 280, y + 6, 5, 8, DARK)
    cv.polygon([(x + 66, y + 33), (x + 384, y + 33), (x + 366, y + h - 2),
                (x + 88, y + h - 2)], (70, 74, 78))
    for wx in range(x + 100, x + 360, 36):                   # deck markings
        cv.rect(wx, y + 28, 16, 3, WHITE)
    # jet climbing away from the deck, drawn last so it stays visible
    cv.polygon([(x + 292, y + 11), (x + 322, y + 3), (x + 315, y + 9),
                (x + 330, y + 12), (x + 298, y + 13)], DARK)
    for wy in (y + h - 8,):
        for wx in range(x + 8, x + w - 8, 30):
            cv.rect(wx, wy, 17, 3, WHITE)


def arena_strip(cv, x, y, w, h):
    """A concert arena: lit stage at one end, the crowd streaming out."""
    cv.rect(x, y, w, h, DARK)
    # stage block with light beams
    cv.rect(x + 8, y + 8, 74, h - 16, (90, 60, 110))
    cv.circle(x + 45, y + 18, 7, YELLOW)
    cv.line(x + 45, y + 18, x + 130, y + 4, GOLD, 2)
    cv.line(x + 45, y + 18, x + 138, y + 30, (232, 120, 160), 2)
    cv.line(x + 45, y + 18, x + 128, y + h - 6, (120, 200, 240), 2)
    # exit sign glowing green
    cv.rect(x + w - 92, y + 6, 52, 14, GREEN)
    cv.text(x + w - 66, y + 9, "EXIT", 1, WHITE, align="center")
    # crowd: rows of heads moving toward the exit
    for row, ry in enumerate((y + h - 26, y + h - 15)):
        for i in range(14):
            hx = x + 118 + i * 26 + (row * 11)
            if hx > x + w - 14:
                break
            cv.circle(hx, ry, 6, (196, 164, 128))
            cv.rect(hx - 6, ry + 6, 12, 5, (90, 110, 140) if i % 2
                    else (140, 90, 90))


def train_picto(cv, x, y, w, h):
    """The Saryu-Kamala Express crossing toward the border."""
    cv.rect(x, y, w, h, (206, 230, 240))
    cv.circle(x + w - 40, y + 14, 10, GOLD)
    cv.rect(x, y + h - 16, w, 16, (146, 180, 120))           # fields
    cv.rect(x, y + h - 16, w, 3, (110, 84, 60))              # track bed
    for tx in range(x + 6, x + w - 6, 22):                   # sleepers
        cv.rect(tx, y + h - 13, 12, 3, (110, 84, 60))
    # locomotive
    lx, ly = x + 26, y + h - 44
    cv.rect(lx, ly, 96, 28, (178, 52, 40))
    cv.rect(lx + 66, ly - 12, 30, 12, (178, 52, 40))         # cab
    cv.rect(lx + 71, ly - 9, 12, 8, SKY)
    cv.rect(lx + 8, ly + 6, 14, 10, GOLD)                    # headlamp panel
    cv.circle(lx + 22, y + h - 14, 7, DARK)
    cv.circle(lx + 84, y + h - 14, 7, DARK)
    # two carriages
    for cx0 in (lx + 104, lx + 196):
        cv.rect(cx0, ly + 2, 84, 26, (52, 110, 170))
        for wx in range(cx0 + 8, cx0 + 76, 16):
            cv.rect(wx, ly + 8, 10, 9, WHITE)
        cv.circle(cx0 + 18, y + h - 14, 7, DARK)
        cv.circle(cx0 + 66, y + h - 14, 7, DARK)
    # tricolour pennant on the loco
    cv.vline(lx + 4, ly - 14, 14, INK)
    cv.rect(lx + 4, ly - 14, 22, 5, (255, 153, 51))
    cv.rect(lx + 4, ly - 9, 22, 5, WHITE)
    cv.rect(lx + 4, ly - 4, 22, 5, (19, 136, 8))


def mic_picto(cv, x, y, w, h):
    """A lone microphone on a dark stage, one spotlight."""
    cv.rect(x, y, w, h, (40, 36, 48))
    cv.polygon([(x + w // 2 - 8, y), (x + w // 2 + 8, y),
                (x + w // 2 + 44, y + h), (x + w // 2 - 44, y + h)],
               (120, 112, 88))
    cx = x + w // 2
    cv.circle(cx, y + 20, 11, (200, 200, 205))               # mic head
    for gy in range(y + 12, y + 28, 4):
        cv.hline(cx - 10, gy, 20, GREY)
    cv.rect(cx - 2, y + 30, 4, 22, (200, 200, 205))          # stem
    cv.line(cx, y + 52, cx - 14, y + h - 6, (200, 200, 205), 3)
    cv.line(cx, y + 52, cx + 14, y + h - 6, (200, 200, 205), 3)
    cv.rect(x, y + h - 6, w, 6, (24, 22, 30))                # stage floor


def baltic_ship_picto(cv, x, y, w, h):
    """A Russian cargo ship ablaze in the Baltic, smoke over the stern."""
    cv.rect(x, y, w, h, (186, 208, 224))
    # smoke
    cv.circle(x + 196, y + 12, 11, GREY)
    cv.circle(x + 226, y + 8, 13, GREY)
    cv.circle(x + 258, y + 14, 10, GREY)
    # hull and container stacks
    by = y + h - 22
    cv.polygon([(x + 30, by), (x + w - 30, by), (x + w - 48, y + h - 6),
                (x + 48, y + h - 6)], (120, 44, 40))
    cv.rect(x + 52, by - 16, 44, 16, (52, 110, 170))
    cv.rect(x + 100, by - 16, 44, 16, (46, 125, 62))
    cv.rect(x + 74, by - 30, 44, 14, (196, 90, 24))
    cv.rect(x + w - 96, by - 24, 40, 24, (210, 210, 214))    # superstructure
    cv.rect(x + w - 88, by - 18, 10, 8, SKY)
    # flames over the stern containers: two narrow tongues of fire
    for fx in (x + 196, x + 228):
        cv.triangle(fx - 15, by - 14, fx, by - 40, fx + 15, by - 14,
                    (196, 90, 24))
        cv.triangle(fx - 9, by - 14, fx, by - 30, fx + 9, by - 14, RED)
        cv.triangle(fx - 4, by - 14, fx, by - 21, fx + 4, by - 14, YELLOW)
    # waves
    for wx in range(x + 8, x + w - 8, 28):
        cv.rect(wx, y + h - 5, 16, 3, WHITE)


# ---------------------------------------------------------------- layout
def kicker(cv, x, y, s, color):
    cv.rect(x, y - 2, text_width(s, 2) + 10, 18, color)
    cv.text(x + 5, y, s, 2, CREAM)


def stat_box(cv, x, y, w, h, value, label):
    cv.frame(x, y, w, h, BURG, 2)
    cv.rect(x + 2, y + 2, w - 4, h - 4, (252, 247, 236))
    cv.text(x + w // 2, y + 8, value, 3, BURG, align="center")
    cv.text(x + w // 2, y + 42, label, 1, INK, align="center")


def draw_page(cv):
    # ---- masthead: burgundy band, gold rules, date in plain sight
    cv.rect(0, 0, W, 148, BURG)
    cv.text(W // 2, 22, "THE WORLD TODAY", 6, CREAM, align="center")
    cv.rect(40, 76, W - 80, 3, GOLD)
    cv.text(W // 2, 90, "TUESDAY 24 NOVEMBER 2026", 3, GOLD, align="center")
    cv.rect(40, 124, W - 80, 2, GOLD)
    cv.text(W // 2, 134, "ONE DAY - ONE PAGE - THE WORLD", 1, CREAM,
            align="center")
    # ---- dateline strip
    cv.text(W // 2, 156,
            "STOCKHOLM \u2022 WASHINGTON \u2022 MANCHESTER \u2022 "
            "AYODHYA \u2022 TEHRAN \u2022 HELSINKI",
            2, INK, align="center")
    cv.rect(24, 178, W - 48, 2, INK)

    # ---- lead story: Europe rallies behind Ukraine in Stockholm
    kicker(cv, 24, 192, "EUROPE - PEACE TALKS", BURG)
    cv.text(24, 218, "EUROPE RALLIES", 4, INK)
    cv.text(24, 248, "BEHIND UKRAINE", 4, INK)
    cv.rect(24, 284, 300, 3, GOLD)
    for i, line in enumerate((
            "TRUMP'S 28-POINT PLAN SPARKS ALARM",
            "LEADERS GATHER IN STOCKHOLM TODAY",
            "ZELENSKY: NO PEACE THAT REWARDS",
            "LAND TAKEN BY FORCE")):
        cv.text(24, 298 + i * 18, line, 2, INK)
    stat_box(cv, 24, 392, 192, 70, "28", "POINTS IN THE PLAN")
    stat_box(cv, 228, 392, 192, 70, "4TH", "CRIMEA PLATFORM SUMMIT")
    stat_box(cv, 432, 392, 188, 70, "STOCKHOLM", "SUMMIT VENUE")
    cv.frame(640, 186, 360, 282, INK, 2)
    stockholm_scene(cv, 642, 188, 356, 278)

    cv.rect(24, 476, W - 48, 2, INK)

    # ---- second row: Venezuela and Manchester
    kicker(cv, 24, 490, "AMERICAS - WASHINGTON", SLATE)
    cv.text(24, 514, "US BRANDS CARTEL", 3, INK)
    cv.text(24, 539, "A TERROR GROUP", 3, INK)
    for i, line in enumerate((
            "CARTEL DE LOS SOLES LISTED",
            "CARRIER SAILS IN CARIBBEAN",
            "21 BOAT STRIKES SINCE SEPTEMBER",
            "83 DEAD; MADURO IN US SIGHTS")):
        cv.text(24, 570 + i * 18, line, 2, INK)
    carrier_strip(cv, 24, 646, 476, 48)

    cv.vline(512, 484, 216, INK)
    kicker(cv, 524, 490, "BRITAIN - MANCHESTER", PLUM)
    cv.text(524, 514, "12,000 EVACUATED", 3, INK)
    cv.text(524, 539, "IN CONCERT SCARE", 3, INK)
    for i, line in enumerate((
            "UNKNOWN SUBSTANCE RELEASED",
            "AT MANCHESTER CONCERT VENUE",
            "POLICE EVACUATE THE CROWD",
            "INVESTIGATION UNDER WAY")):
        cv.text(524, 570 + i * 18, line, 2, INK)
    arena_strip(cv, 524, 646, 476, 48)

    cv.rect(24, 708, W - 48, 2, INK)

    # ---- third row: three short stories
    cols = [
        (24, 336, "INDIA - NEPAL", ORANGE, train_picto,
         ("FIRST TRAIN LINKS", "AYODHYA-JANAKPUR"),
         ("MODI AND SHAH FLAG OFF", "SARYU-KAMALA EXPRESS",
          "NEW CROSS-BORDER LINE")),
        (352, 664, "IRAN - TEHRAN", RUST, mic_picto,
         ("SINGER GETS 74", "LASHES FOR CONCERT"),
         ("PARASTOO AHMADI SENTENCED", "74 LASHES FOR EACH OF FIVE",
          "VIRTUAL CONCERT CASE")),
        (680, 1000, "BALTIC - FINLAND", SLATE, baltic_ship_picto,
         ("RUSSIAN SHIP BURNS", "OFF FINLAND"),
         ("FINLAND CONFIRMS THE HIT", "VESSEL STRUCK BY DRONES",
          "MOSCOW HAULS SHIP AWAY")),
    ]
    for x0, x1, kick, color, picto, head, subs in cols:
        picto(cv, x0, 716, x1 - x0, 70)
        kicker(cv, x0, 796, kick, color)
        for i, line in enumerate(head):
            cv.text(x0, 814 + i * 16, line, 2, INK)
        for i, line in enumerate(subs):
            cv.text(x0, 852 + i * 18, line, 2, INK)
    cv.vline(344, 716, 204, INK)
    cv.vline(672, 716, 204, INK)

    cv.rect(24, 928, W - 48, 2, INK)

    # ---- bottom strip: Brazil and business in brief
    cv.rect(0, 936, W, 88, BURG_DARK)
    cv.text(W // 2, 948,
            "BOLSONARO BACK IN JAIL IN BRAZIL \u2022 "
            "FERRARI SHOWS 296 TWINS IN SPAIN",
            2, CREAM, align="center")
    cv.text(W // 2, 974, "NVIDIA SOARS AS JENSEN HUANG RETURNS AS CEO",
            2, GOLD, align="center")


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    data = encode_png(cv)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

