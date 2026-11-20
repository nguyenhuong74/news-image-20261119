#!/usr/bin/env python3
"""The World in One Page -- Thursday 19 November 2026.

Draws a one-page newspaper front page summing up 19 November 2026's
world news as a 1024x1024 PNG, using only the Python standard library.

Everything is drawn in code: a hand-written 5x7 bitmap font, simple
geometric pictograms, and a PNG encoder built from zlib + struct.
No network, no clock, no randomness -- two runs write byte-identical
files.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one row per string, "#" = ink.  Only capitals are
# stored; draw_text() upper-cases its input first.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# Colours (R, G, B).
PAPER = (253, 246, 227)   # newsprint cream
INK = (24, 24, 24)        # near-black
RED = (178, 34, 34)       # headline red
BLUE = (28, 68, 142)      # deep blue
GREY = (110, 108, 100)    # muted grey
LIGHT = (238, 228, 205)   # pale panel fill
GOLD = (196, 141, 26)     # accent gold
TEAL = (18, 110, 105)     # teal accent


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def hline(self, x, y, length, c, thick=1):
        self.fill(x, y, length, thick, c)

    def vline(self, x, y, length, c, thick=1):
        self.fill(x, y, thick, length, c)

    def rect(self, x, y, w, h, c, thick=1):
        self.hline(x, y, w, c, thick)
        self.hline(x, y + h - thick, w, c, thick)
        self.vline(x, y, h, c, thick)
        self.vline(x + w - thick, y, h, c, thick)

    def line(self, x0, y0, x1, y1, c, thick=1):
        # Bresenham line.
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.px(xx, yy, c)
                else:
                    if (r - 1) ** 2 <= d2 <= r * r:
                        self.px(xx, yy, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        # Scanline fill of a triangle.
        ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / max(1, cy - by)
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            for x in range(lo, hi + 1):
                self.px(x, y, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    """Draw upper-cased text at (x, y); returns the x just past the text."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = cur + " " + word if cur else word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_chars, leading):
    """Draw a wrapped paragraph; returns the y just below it."""
    for line in wrap_text(s, max_chars):
        draw_text(cv, x, y, line, scale, color)
        y += 7 * scale + leading
    return y


# ------------------------------------------------------------------- PNG
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- pictograms
def pic_summit(cv, x, y, s):
    """Globe with three leaders' markers: the Shenzhen trilateral."""
    cx, cy, r = x + 90 * s // 10, y + 55 * s // 10, 48 * s // 10
    cv.circle(cx, cy, r, BLUE, filled=False)
    cv.circle(cx, cy, r - 3, BLUE, filled=False)
    cv.vline(cx, cy - r, 2 * r, BLUE)
    cv.hline(cx - r, cy, 2 * r, BLUE)
    cv.circle(cx, cy, r // 2, BLUE, filled=False)
    # Three summit markers around the globe.
    for dx, dy, col in ((-52, -42, RED), (0, -56, GOLD), (52, -42, TEAL)):
        mx, my = cx + dx * s // 10, cy + dy * s // 10
        cv.circle(mx, my, 7 * s // 10, col)
        cv.circle(mx, my, 3 * s // 10, PAPER)
    # Handshake arc beneath.
    cv.line(cx - 34 * s // 10, cy + 40 * s // 10,
            cx, cy + 26 * s // 10, INK, 3)
    cv.line(cx, cy + 26 * s // 10,
            cx + 34 * s // 10, cy + 40 * s // 10, INK, 3)


def pic_scales(cv, x, y, s):
    """Scales of justice: the ICJ genocide ruling."""
    cx = x + 60 * s // 10
    top = y + 8 * s // 10
    cv.vline(cx, top, 78 * s // 10, INK, 3)
    cv.hline(cx - 46 * s // 10, top + 6 * s // 10, 92 * s // 10, INK, 3)
    cv.circle(cx, top + 2 * s // 10, 5 * s // 10, GOLD)
    for side in (-1, 1):
        px = cx + side * 42 * s // 10
        cv.line(px, top + 6 * s // 10, px - 16 * s // 10,
                top + 44 * s // 10, INK, 2)
        cv.line(px, top + 6 * s // 10, px + 16 * s // 10,
                top + 44 * s // 10, INK, 2)
        cv.hline(px - 18 * s // 10, top + 44 * s // 10, 36 * s // 10, GOLD, 4)
    cv.hline(cx - 30 * s // 10, top + 82 * s // 10, 60 * s // 10, INK, 4)


def pic_bridge(cv, x, y, s):
    """The Kerch Bridge, broken in the middle, over the strait."""
    y0 = y + 30 * s // 10
    # Left deck and right deck with a gap.
    cv.fill(x, y0, 78 * s // 10, 8 * s // 10, INK)
    cv.fill(x + 112 * s // 10, y0, 78 * s // 10, 8 * s // 10, INK)
    # Fallen span, tilted into the water.
    cv.line(x + 82 * s // 10, y0 + 4 * s // 10,
            x + 106 * s // 10, y0 + 52 * s // 10, INK, 4)
    # Arch and pylons.
    cv.line(x + 8 * s // 10, y0, x + 8 * s // 10, y0 - 26 * s // 10, INK, 3)
    cv.line(x + 182 * s // 10, y0, x + 182 * s // 10, y0 - 26 * s // 10,
            INK, 3)
    cv.line(x + 8 * s // 10, y0 - 26 * s // 10,
            x + 95 * s // 10, y0 - 44 * s // 10, INK, 2)
    cv.line(x + 182 * s // 10, y0 - 26 * s // 10,
            x + 95 * s // 10, y0 - 44 * s // 10, INK, 2)
    # Blast burst above the gap.
    bx, by = x + 95 * s // 10, y0 - 8 * s // 10
    for dx, dy in ((-14, 0), (14, 0), (0, -14), (0, 10), (-10, -10),
                   (10, -10), (-10, 8), (10, 8)):
        cv.line(bx, by, bx + dx * s // 10, by + dy * s // 10, RED, 2)
    cv.circle(bx, by, 5 * s // 10, RED)
    # Water.
    for k in range(3):
        yy = y0 + 58 * s // 10 + k * 9 * s // 10
        cv.hline(x + 6 * s // 10 + (k % 2) * 12, yy, 170 * s // 10, BLUE, 2)


def pic_chart(cv, x, y, s):
    """Rising bars and a record arrow: the Anthropic IPO."""
    base = y + 84 * s // 10
    heights = (22, 38, 54, 74)
    for i, hh in enumerate(heights):
        bx = x + 12 * s // 10 + i * 42 * s // 10
        col = TEAL if i < 3 else GOLD
        cv.fill(bx, base - hh * s // 10, 30 * s // 10, hh * s // 10, col)
    cv.hline(x + 6 * s // 10, base, 180 * s // 10, INK, 3)
    cv.line(x + 14 * s // 10, base - 20 * s // 10,
            x + 172 * s // 10, base - 80 * s // 10, RED, 3)
    cv.triangle(x + 172 * s // 10, base - 92 * s // 10,
                x + 150 * s // 10, base - 78 * s // 10,
                x + 172 * s // 10, base - 66 * s // 10, RED)


def pic_flame(cv, x, y, s):
    """Flame over a building: the Bangladesh lockdown violence."""
    # Building.
    bx, by = x + 28 * s // 10, y + 52 * s // 10
    cv.fill(bx, by, 90 * s // 10, 46 * s // 10, GREY)
    cv.rect(bx, by, 90 * s // 10, 46 * s // 10, INK, 2)
    for r in range(2):
        for c in range(3):
            cv.fill(bx + 10 * s // 10 + c * 28 * s // 10,
                    by + 10 * s // 10 + r * 20 * s // 10,
                    12 * s // 10, 10 * s // 10, PAPER)
    # Flame.
    fx = x + 73 * s // 10
    cv.triangle(fx - 26 * s // 10, by, fx, by - 46 * s // 10,
                fx + 26 * s // 10, by, RED)
    cv.triangle(fx - 14 * s // 10, by, fx + 4 * s // 10, by - 30 * s // 10,
                fx + 18 * s // 10, by, GOLD)
    cv.triangle(fx - 6 * s // 10, by, fx, by - 16 * s // 10,
                fx + 8 * s // 10, by, PAPER)


def pic_ice(cv, x, y, s):
    """Ice peaks and a shield: the Greenland security deal."""
    base = y + 88 * s // 10
    cv.triangle(x + 6 * s // 10, base, x + 58 * s // 10, base - 62 * s // 10,
                x + 110 * s // 10, base, BLUE)
    cv.triangle(x + 70 * s // 10, base, x + 122 * s // 10, base - 46 * s // 10,
                x + 178 * s // 10, base, TEAL)
    cv.triangle(x + 44 * s // 10, base - 46 * s // 10,
                x + 58 * s // 10, base - 62 * s // 10,
                x + 72 * s // 10, base - 46 * s // 10, PAPER)
    # Shield with a star above the peaks.
    sx, sy = x + 140 * s // 10, y + 6 * s // 10
    cv.triangle(sx - 16 * s // 10, sy, sx + 16 * s // 10, sy,
                sx, sy + 26 * s // 10, GOLD)
    cv.circle(sx, sy + 12 * s // 10, 4 * s // 10, PAPER)


def pic_tank(cv, x, y, s):
    """Small tank: the Gaza raid."""
    cv.fill(x, y + 14 * s // 10, 34 * s // 10, 10 * s // 10, INK)
    cv.fill(x + 8 * s // 10, y + 6 * s // 10, 14 * s // 10, 10 * s // 10, INK)
    cv.hline(x + 20 * s // 10, y + 10 * s // 10, 16 * s // 10, INK, 3)
    for i in range(3):
        cv.circle(x + 8 * s // 10 + i * 10 * s // 10, y + 28 * s // 10,
                  3 * s // 10, INK)


def pic_atom(cv, x, y, s):
    """Atom: the IAEA warning on Yongbyon."""
    cx, cy = x + 18 * s // 10, y + 16 * s // 10
    cv.circle(cx, cy, 4 * s // 10, RED)
    for r in (12, 15):
        cv.circle(cx, cy, r * s // 10, BLUE, filled=False)
    cv.line(cx - 12 * s // 10, cy - 12 * s // 10,
            cx + 12 * s // 10, cy + 12 * s // 10, BLUE, 2)
    cv.line(cx - 12 * s // 10, cy + 12 * s // 10,
            cx + 12 * s // 10, cy - 12 * s // 10, BLUE, 2)


def pic_boat(cv, x, y, s):
    """Capsized boat and waves: the Senegal sinking."""
    cv.triangle(x + 2 * s // 10, y + 12 * s // 10,
                x + 34 * s // 10, y + 12 * s // 10,
                x + 8 * s // 10, y + 22 * s // 10, INK)
    cv.line(x + 2 * s // 10, y + 12 * s // 10,
            x + 34 * s // 10, y + 12 * s // 10, RED, 2)
    for k in range(2):
        yy = y + 26 * s // 10 + k * 6 * s // 10
        cv.hline(x, yy, 36 * s // 10, BLUE, 2)


# ---------------------------------------------------------------- layout
def story_block(cv, x, y, w, h, kicker, headline, body, pic, pic_s=10):
    """One story cell: kicker, headline, pictogram, body text."""
    cv.rect(x, y, w, h, INK, 2)
    cv.fill(x + 2, y + 2, w - 4, 20, LIGHT)
    draw_text(cv, x + 10, y + 7, kicker, 1, RED)
    hy = draw_para(cv, x + 10, y + 30, headline, 2, INK,
                   (w - 20) // 12, 4)
    px, py = x + 10, hy
    pic(cv, px, py, pic_s)
    tx = px + 200 * pic_s // 10 + 8
    draw_para(cv, tx, hy + 6, body, 1, INK, (x + w - tx - 10) // 6, 3)


def brief(cv, x, y, w, kicker, text, pic, pic_s=10):
    draw_text(cv, x + 48, y, kicker, 1, RED)
    draw_para(cv, x + 48, y + 12, text, 1, INK, (w - 58) // 6, 2)
    pic(cv, x, y - 2, pic_s)


def build():
    cv = Canvas(W, H, PAPER)
    M = 24                      # outer margin
    CW = W - 2 * M              # content width

    # ---- Masthead ------------------------------------------------------
    cv.hline(M, 18, CW, INK, 4)
    draw_centered(cv, W // 2, 30, "THE WORLD IN ONE PAGE", 5, INK)
    draw_centered(cv, W // 2, 74, "THURSDAY 19 NOVEMBER 2026", 2, RED)
    draw_centered(cv, W // 2, 96, "SIX STORIES AND THREE BRIEFS FROM ONE DAY",
                  1, GREY)
    cv.hline(M, 116, CW, INK, 4)
    cv.hline(M, 121, CW, INK, 1)

    # ---- Lead story: the Shenzhen summit ------------------------------
    ly, lh = 132, 218
    cv.rect(M, ly, CW, lh, INK, 3)
    cv.fill(M + 3, ly + 3, CW - 6, 22, LIGHT)
    draw_text(cv, M + 12, ly + 10, "LEAD  -  SHENZHEN, CHINA", 1, RED)
    draw_text(cv, M + 12, ly + 36,
              "THREE POWERS, ONE TABLE", 3, INK)
    pic_summit(cv, M + 24, ly + 84, 10)
    tx = M + 260
    after = draw_para(cv, tx, ly + 84,
                      "Trump, Xi and Putin hold the first-ever three-way summit "
                      "on the APEC sidelines. Their joint declaration pledges "
                      "dialogue on nuclear risks and says a nuclear war cannot "
                      "be won and must never be fought. No deal on Ukraine.",
                      1, INK, (M + CW - tx - 16) // 6, 4)
    draw_para(cv, tx, after + 14,
              "China and Russia call the talks constructive; Washington "
              "calls them a first conversation, not a negotiation.",
              1, GREY, (M + CW - tx - 16) // 6, 4)

    # ---- Grid of five stories + numbers box ---------------------------
    gy = 366
    gw = (CW - 16) // 2
    gh = 148
    rows = [
        ("THE HAGUE  -  JUSTICE",
         "MYANMAR GUILTY OF GENOCIDE",
         "The UN's top court rules 9-6 that Myanmar committed "
         "genocide against the Rohingya in 2017 -- the first time "
         "it has held a state guilty. Reparations and return ordered.",
         pic_scales),
        ("KERCH STRAIT  -  WAR",
         "BRIDGE HIT A THIRD TIME",
         "Ukraine strikes the Crimean Bridge again, this time its "
         "rail section, with Neptune missiles. Trains halt; road "
         "traffic already shut since Tuesday's span collapse.",
         pic_bridge),
        ("NEW YORK  -  MARKETS",
         "ANTHROPIC: BIGGEST IPO EVER",
         "The Claude maker debuts on Nasdaq at $83 a share, raising "
         "$81.3 billion -- topping SpaceX -- at a $1.5 trillion "
         "valuation. First frontier AI lab to go public.",
         pic_chart),
        ("DHAKA  -  UNREST",
         "BANGLADESH BURNS, FOUR DEAD",
         "A banned Awami League lockdown brings bombs, arson and "
         "clashes to 28 districts. Nobel laureate Yunus's ancestral "
         "home is torched in Chattogram.",
         pic_flame),
        ("COPENHAGEN  -  ARCTIC",
         "GREENLAND DEAL PASSES 109-0",
         "Denmark's parliament unanimously ratifies the US security "
         "deal for Greenland, clearing the way for more American "
         "bases and the Golden Dome shield. No vote against.",
         pic_ice),
    ]
    for i, (kick, head, body, pic) in enumerate(rows):
        gx = M + (i % 2) * (gw + 16)
        gyy = gy + (i // 2) * (gh + 12)
        story_block(cv, gx, gyy, gw, gh, kick, head, body, pic)

    # Numbers box in the sixth cell.
    nx = M + gw + 16
    ny = gy + 2 * (gh + 12)
    cv.rect(nx, ny, gw, gh, INK, 2)
    cv.fill(nx + 2, ny + 2, gw - 4, 20, LIGHT)
    draw_text(cv, nx + 10, ny + 7, "THE DAY IN NUMBERS", 1, RED)
    nums = [("$81.3B", "Anthropic IPO, a record"),
            ("9 - 6", "ICJ vote on Myanmar"),
            ("109 - 0", "Denmark on Greenland"),
            ("3rd", "strike on Kerch Bridge"),
            ("4", "killed in Bangladesh")]
    yy = ny + 32
    for big, small in nums:
        draw_text(cv, nx + 12, yy, big, 2, INK)
        draw_text(cv, nx + 130, yy + 3, small, 1, GREY)
        yy += 20

    # ---- Briefs strip ---------------------------------------------------
    by = gy + 3 * (gh + 12) + 4
    cv.hline(M, by, CW, INK, 3)
    draw_text(cv, M, by + 10, "IN BRIEF", 2, RED)
    bw = (CW - 32) // 3
    briefs = [
        ("GAZA", "Israel says its first ground raid past the Gaza "
         "ceasefire line is over. Tanks crossed near Nuseirat to "
         "destroy a tunnel; about 6,000 people fled.", pic_tank),
        ("YONGBYON", "The IAEA says North Korea has expanded its "
         "uranium enrichment plant at Yongbyon, a serious concern "
         "for the nuclear watchdog.", pic_atom),
        ("SENEGAL", "Dozens missing after a migrant boat carrying "
         "50 to 100 people capsizes off Yenne, south of Dakar. "
         "Four bodies recovered.", pic_boat),
    ]
    for i, (kick, text, pic) in enumerate(briefs):
        bx = M + i * (bw + 16)
        brief(cv, bx, by + 38, bw, kick, text, pic)
        if i:
            cv.vline(bx - 8, by + 36, 84, GREY, 1)

    # ---- Footer ----------------------------------------------------------
    fy = by + 136
    cv.hline(M, fy, CW, INK, 2)
    draw_centered(cv, W // 2, fy + 10,
                  "DRAWN IN CODE  -  NO PHOTOGRAPHS  -  SOURCES: REUTERS, "
                  "AP, BBC, DPA, IAEA, UNITED NATIONS", 1, GREY)
    draw_centered(cv, W // 2, fy + 24,
                  "THE WORLD IN ONE PAGE  -  19 NOVEMBER 2026", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print(f"wrote {path}: {cv.w}x{cv.h}, {size} bytes")


if __name__ == "__main__":
    main()
