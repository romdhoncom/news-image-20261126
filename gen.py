#!/usr/bin/env python3
"""THE WORLD TODAY — Thursday 26 November 2026, morning edition.

Pure Python standard library only (os, struct, sys, zlib): own raster
canvas, own 5x7 bitmap font, own PNG encoder. No PIL, no network.
Draws a 1024x1024 newspaper front page and writes entry.png.
Deterministic: identical bytes on every run.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (246, 241, 230)
CARD = (252, 250, 244)
INK = (22, 22, 26)
NAVY = (22, 35, 63)
NAVY2 = (34, 52, 92)
RED = (178, 34, 34)
GOLD = (216, 169, 60)
GREY = (110, 108, 100)
LGREY = (168, 164, 152)
WHITE = (250, 248, 242)
DARK = (28, 28, 34)
SKY = (176, 206, 228)
SKY2 = (120, 165, 205)
SEA = (64, 110, 150)
FLAME = (232, 122, 28)
FLAME2 = (244, 196, 66)
GREEN = (46, 125, 72)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = c[0]
            self.pix[i + 1] = c[1]
            self.pix[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pix[i] = c[0]
                self.pix[i + 1] = c[1]
                self.pix[i + 2] = c[2]

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.px(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for a in range(0, 360):
            import math
            rad = math.radians(a)
            for k in range(t):
                self.px(int(cx + (r - k) * math.cos(rad)),
                       int(cy + (r - k) * math.sin(rad)), c)


def png_bytes(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.pix[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
            chunk(b"IEND", b""))


# --- 5x7 bitmap font: each glyph is 7 rows of 5 bits, bit 4 = left ---
FONT = {
    ' ': [0, 0, 0, 0, 0, 0, 0],
    '!': [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    '"': [0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00],
    '#': [0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A],
    '$': [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    '%': [0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x18],
    '&': [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "'": [0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00],
    '(': [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ')': [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    '*': [0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00],
    '+': [0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00],
    ',': [0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08],
    '-': [0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00],
    '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    '/': [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    '0': [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    '1': [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    '3': [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    '5': [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    '6': [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    '7': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    '8': [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    '9': [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    ':': [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
    ';': [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08],
    '<': [0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02],
    '=': [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
    '>': [0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08],
    '?': [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    '@': [0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E],
    'A': [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'B': [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    'C': [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    'D': [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    'E': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    'F': [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    'G': [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    'H': [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    'J': [0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E],
    'K': [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    'L': [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
}

FONT.update({
    'N': [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    'O': [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'P': [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    'Q': [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    'R': [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    'S': [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    'T': [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    'U': [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    'V': [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    'W': [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    'X': [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    'Y': [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    'Z': [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    '[': [0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E],
    '\\': [0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01],
    ']': [0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E],
    '^': [0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00],
    '_': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
    '`': [0x08, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00],
    '{': [0x02, 0x04, 0x04, 0x08, 0x04, 0x04, 0x02],
    '|': [0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    '}': [0x08, 0x04, 0x04, 0x02, 0x04, 0x04, 0x08],
    '~': [0x00, 0x00, 0x0E, 0x15, 0x00, 0x00, 0x00],
    '·': [0x00, 0x04, 0x04, 0x00, 0x00, 0x00, 0x00],
})

ALIASES = {'—': '-', '–': '-', '’': "'", '‘': "'", '“': '"', '”': '"',
           '…': '.', '×': 'x', '•': '·'}
for _lo in 'abcdefghijklmnopqrstuvwxyz':
    FONT[_lo] = FONT[_lo.upper()]


def glyph(ch):
    ch = ALIASES.get(ch, ch)
    return FONT.get(ch, FONT['?'])


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, color):
    for ch in s:
        g = glyph(ch)
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row & (0x10 >> c):
                    cv.rect(x + c * scale, y + r * scale, scale, scale, color)
        x += 6 * scale


def draw_center(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def draw_right(cv, x, y, s, scale, color):
    draw_text(cv, x - text_w(s, scale), y, s, scale, color)


def cross(cv, cx, cy, s, color, t=2):
    cv.rect(cx - s, cy - t // 2, 2 * s + 1, t, color)
    cv.rect(cx - t // 2, cy - s, t, 2 * s + 1, color)


# --- lead pictures --------------------------------------------------------
def pic_tariffs(cv, x, y, w, h):
    # Bar chart: CHINA 40, EU 15, BRAZIL 10 — new US duties on 14 partners.
    base = y + h - 26
    cv.rect(x, base, w, 2, INK)
    bars = [("CHINA", 40, RED), ("EU", 15, NAVY2), ("BRAZIL", 10, GOLD)]
    slot = w // 3
    for i, (name, val, col) in enumerate(bars):
        bx = x + i * slot + 18
        bw = slot - 36
        bh = int(val * 3.1)
        cv.rect(bx, base - bh, bw, bh, col)
        draw_center(cv, bx + bw // 2, base - bh - 18, str(val) + "%", 2, INK)
        draw_center(cv, bx + bw // 2, base + 6, name, 1, INK)


def pic_wardead(cv, x, y, w, h):
    # Row of small crosses over a dark field, under the big number.
    n = 11
    gap = w // (n + 1)
    for i in range(n):
        cx = x + gap * (i + 1)
        cross(cv, cx, y + h // 2, 9, (96, 96, 108), 3)
    cv.hline(x + 10, y + h - 8, w - 20, (70, 70, 82), 2)


def pic_fire(cv, x, y, w, h):
    # Night road, tanker truck, flames.
    cv.rect(x, y, w, h, (32, 32, 40))
    cv.rect(x, y + h - 22, w, 22, (58, 58, 66))  # road
    cv.hline(x, y + h - 22, w, GOLD, 2)
    # tanker
    tx, ty = x + 30, y + h - 62
    cv.rect(tx, ty, 150, 34, (200, 200, 205))          # tank
    cv.rect(tx + 150, ty + 10, 44, 24, RED)            # cab
    cv.rect(tx + 158, ty + 14, 18, 12, SKY)            # cab window
    cv.disc(tx + 30, ty + 40, 9, INK)
    cv.disc(tx + 70, ty + 40, 9, INK)
    cv.disc(tx + 165, ty + 40, 9, INK)
    # flames licking from the tank: narrow, staggered, tapered tips
    for fx, fh, fc in [(tx + 24, 34, FLAME), (tx + 58, 44, FLAME2),
                       (tx + 92, 38, FLAME), (tx + 122, 28, FLAME2)]:
        cv.rect(fx, ty - fh, 11, fh, fc)
        cv.rect(fx + 3, ty - fh - 8, 5, 9, FLAME2)
        cv.rect(fx + 4, ty - fh - 13, 3, 6, (250, 240, 180))
    # thin smoke wisps, high and small
    cv.disc(tx + 62, y + 12, 7, (110, 110, 120))
    cv.disc(tx + 84, y + 6, 6, (130, 130, 140))


def pic_space(cv, x, y, w, h):
    # Earth arc below, rocket climbing, satellite dots in orbit.
    # Everything stays inside the (x, y, w, h) picture box.
    cv.rect(x, y, w, h, (14, 22, 44))
    # stars
    for sx, sy in [(18, 14), (52, 30), (96, 10), (240, 26), (280, 12),
                   (36, 52), (262, 58), (120, 8), (210, 56)]:
        cv.rect(x + sx, y + sy, 3, 3, WHITE)
    cx = x + w // 2
    # orbit ring, small, centred on the rocket
    cv.ring(cx, y + 46, 38, GOLD, 2)
    # satellites on the ring (left, right, top)
    for sx, sy in [(cx - 40, y + 44), (cx + 32, y + 44), (cx - 4, y + 6)]:
        cv.rect(sx, sy, 9, 5, GOLD)
        cv.rect(sx - 7, sy + 1, 6, 3, SKY2)
        cv.rect(sx + 10, sy + 1, 6, 3, SKY2)
    # earth arc: a disc fully inside the picture box, peeking over its
    # bottom edge like a horizon (centre just below the box's bottom).
    cv.disc(cx, y + h - 2, 40, SEA)
    cv.disc(cx - 20, y + h - 10, 8, GREEN)
    cv.disc(cx + 22, y + h - 14, 6, GREEN)
    # rocket, small, climbing through the ring
    rx, ry = cx - 6, y + 26
    cv.rect(rx, ry, 12, 30, WHITE)
    cv.rect(rx + 4, ry - 9, 4, 9, RED)
    cv.rect(rx - 6, ry + 20, 6, 10, RED)
    cv.rect(rx + 12, ry + 20, 6, 10, RED)
    cv.rect(rx + 4, ry + 30, 4, 10, FLAME)
    cv.rect(rx + 5, ry + 30, 2, 14, FLAME2)


def pic_flags(cv, x, y, w, h):
    # UK flag (left) and EU flag (right), side by side.
    fw, fh = (w - 24) // 2, h - 8
    ux, uy = x + 4, y + 4
    ex, ey = x + 12 + fw, y + 4
    # UK: blue field, white and red crosses
    cv.rect(ux, uy, fw, fh, NAVY2)
    cv.rect(ux, uy + fh // 2 - 9, fw, 18, WHITE)
    cv.rect(ux + fw // 2 - 9, uy, 18, fh, WHITE)
    cv.rect(ux, uy + fh // 2 - 5, fw, 10, RED)
    cv.rect(ux + fw // 2 - 5, uy, 10, fh, RED)
    # EU: blue field, circle of gold stars
    cv.rect(ex, ey, fw, fh, NAVY)
    import math
    cx, cy = ex + fw // 2, ey + fh // 2
    r = min(fw, fh) // 2 - 12
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx = int(cx + r * math.cos(a))
        sy = int(cy + r * math.sin(a))
        cv.disc(sx, sy, 4, GOLD)


# --- layout ----------------------------------------------------------------
MORE = [
    "UKRAINE HITS 5 RUSSIAN JETS AT SAVASLEYKA AIR BASE",
    "THANKSGIVING: TRUMP PARDONS TURKEYS FREEDOM, FEATHERS",
    "S&P PUTS NVIDIA ON DOWNGRADE WATCH; STOCK DOWN 3.9%",
    "HOUTHIS HIT SAUDI ARABIA'S BIGGEST REFINERY; BRENT $94.81",
    "KIM JONG UN SEEKS WIDER TACTICAL NUCLEAR DEPLOYMENT",
    "SOLOMON ISLANDS SIGNS SECURITY TREATY WITH AUSTRALIA",
    "RAMAPHOSA WINS REPRIEVE IN FARMGATE IMPEACHMENT PROBE",
    "LEBANON TO OPEN A SECOND INTERNATIONAL AIRPORT",
    "SECOND JUDGE BLOCKS TRUMP BIRTHRIGHT CITIZENSHIP ORDER",
    "US THIRD-QUARTER GDP REVISED SHARPLY HIGHER",
    "SUDAN DRONE STRIKES KILL 19 CIVILIANS IN BLUE NILE",
    "ISRAELI STRIKE IN GAZA KILLS SENIOR HAMAS OFFICIAL",
    "BANGLADESH RAISES GARMENT WAGES 36%",
    "DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65",
    "COLOMBIA POLICE FREE 20 HOSTAGES AFTER 17-HOUR SIEGE",
    "KENYA'S LAST EBOLA PATIENT OUT; DRC TOLL PASSES 5,300",
    "NORWAY COURT VOIDS CLIMATE-DISPUTED OIL LICENCES",
    "GHANA UNVEILS HERITAGE SERIES BANKNOTES",
    "SHENZHOU-24 DOCKS WITH FIRST FOREIGN ASTRONAUT",
    "MALAYSIA SUES GOOGLE FOR $146M OVER YOUTUBE CONTENT",
    "AUSTRALIA: PLATFORMS MUST REMOVE HARMFUL CONTENT",
    "POLAND PLANS NO-FLY ZONE ON UKRAINE BORDER",
    "GUKESH-SINDAROV CHESS GAME 2 DRAWN; MATCH TIED 1-1",
    "POUNDLAND COLLAPSES, PUTTING 11,000 JOBS AT RISK",
]


def panel(cv, x, y, w, h, bg=CARD):
    cv.rect(x, y, w, h, bg)
    cv.border(x, y, w, h, INK, 2)


def build():
    cv = Canvas(W, H, PAPER)
    cv.border(0, 0, W, H, INK, 4)

    # masthead
    cv.rect(4, 4, 1016, 96, NAVY)
    draw_center(cv, 512, 20, "THE WORLD TODAY", 5, WHITE)
    draw_center(cv, 512, 66, "THURSDAY 26 NOVEMBER 2026  |  MORNING EDITION",
                2, GOLD)
    cv.rect(4, 104, 1016, 4, RED)

    # ---- lead row 1: two big leads ----
    # A: tariffs
    ax, ay, aw, ah = 8, 116, 500, 336
    panel(cv, ax, ay, aw, ah)
    draw_text(cv, ax + 16, ay + 14, "TRADE WAR", 2, RED)
    for i, ln in enumerate(["TRUMP UNVEILS SWEEPING",
                            "NEW TARIFFS ON 14",
                            "PARTNERS"]):
        draw_text(cv, ax + 16, ay + 40 + i * 26, ln, 3, INK)
    pic_tariffs(cv, ax + 16, ay + 140, aw - 32, 160)
    draw_center(cv, ax + aw // 2, ay + 312,
                "WASHINGTON TARGETS 'EXCESS CAPACITY'", 1, GREY)

    # B: war dead (dark panel)
    bx, by, bw, bh = 516, 116, 500, 336
    panel(cv, bx, by, bw, bh, DARK)
    draw_text(cv, bx + 16, by + 14, "UKRAINE WAR", 2, GOLD)
    draw_center(cv, bx + bw // 2, by + 48, "490,334", 5, GOLD)
    draw_center(cv, bx + bw // 2, by + 100, "RUSSIA'S WAR DEAD NEAR", 3, WHITE)
    draw_center(cv, bx + bw // 2, by + 126, "HALF A MILLION", 3, WHITE)
    pic_wardead(cv, bx + 16, by + 180, bw - 32, 120)
    draw_center(cv, bx + bw // 2, by + 312,
                "LEAKED RUSSIAN MORTALITY DATA - BBC", 1, LGREY)

    # ---- lead row 2: three leads ----
    def small_lead(x, y, w, pic, kicker, heads, subs, foot):
        panel(cv, x, y, w, 256)
        pic(cv, x + 8, y + 8, w - 16, 96)
        draw_text(cv, x + 16, y + 114, kicker, 2, RED)
        for i, ln in enumerate(heads):
            draw_text(cv, x + 16, y + 138 + i * 18, ln, 2, INK)
        for i, ln in enumerate(subs):
            draw_text(cv, x + 16, y + 186 + i * 12, ln, 1, GREY)
        draw_text(cv, x + 16, y + 226, foot, 1, INK)

    small_lead(8, 460, 332, pic_fire, "EGYPT",
               ["31 KILLED IN CAIRO", "TANKER FIRE"],
               ["FUEL TANKER CRASHES AND", "EXPLODES ON RING ROAD"],
               "39 AMBULANCES SENT")
    small_lead(348, 460, 328, pic_space, "SPACE",
               ["FCC CLEARS SPACEX FOR", "1 MILLION SATELLITES"],
               ["ORBITAL AI DATA CENTRES", "CALLED 'STARMIND'"],
               "FIRST LAUNCH BY 2033")
    small_lead(684, 460, 332, pic_flags, "EUROPE",
               ["UK AND EU AGREE", "RESET DEAL"],
               ["FOOD TRADE, YOUTH", "MOBILITY, CARBON"],
               "100,000 YOUNG PEOPLE")

    # ---- more from the morning ----
    draw_text(cv, 16, 728, "MORE FROM THE MORNING", 2, INK)
    cv.rect(16, 746, 992, 2, RED)
    for i, item in enumerate(MORE):
        col = 0 if i < 12 else 1
        row = i % 12
        ix = 16 if col == 0 else 524
        iy = 756 + row * 16
        cv.rect(ix, iy + 1, 4, 4, GOLD)
        draw_text(cv, ix + 10, iy, item, 1, INK)

    # ---- footer strip ----
    cv.rect(4, 960, 1016, 56, NAVY)
    draw_text(cv, 16, 978, "REPORTED THURSDAY 26 NOVEMBER 2026", 2, WHITE)
    draw_right(cv, 1008, 978, "SOURCES: REUTERS - AP - BBC", 2, GOLD)
    return cv


def main():
    cv = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    data = png_bytes(cv)
    with open(out, "wb") as f:
        f.write(data)
    import hashlib
    print("wrote", out, len(data), "bytes, sha256",
          hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
