"""Draw the error-screen animations for dunne.systems.

Every screen starts from the last frame of dialing-connect.gif (the
"Connected" dialog) and acts out its error at the art's 2x pixel scale:

  404      the PC searches the rack in a panic and gives up; an orange cat
           and a beige computer mouse chase each other in the background
  offline  three dial attempts and NO DIALTONE: the cat chewed the fiber
  403      requests bounce off a locked cage; the cat paws at the padlock
  500      the rack catches fire; cat and mouse flee
  503      LEDs go dark, a MAINTENANCE sign drops; the cat naps on the CRT
  418      the rack turns into a teapot; the cat sits by it

  python3 errorgifs.py BASE.png OUTDIR [screen ...]
writes OUTDIR/dialing-<screen>.gif (plays once), dialing-<screen>-loop.gif
and dialing-<screen>-end.png (still, for reduced motion).
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFont

BASE, OUT = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3:]

TEAL = (0, 128, 128)
SHADOW = (0, 98, 98)
GRAY = (192, 192, 192)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 0, 128)
AMBER = (240, 160, 32)
RED = (128, 0, 0)
SCENE = (16, 52, 624, 322)            # teal scene, x0 y0 x1 y1 (exclusive)
RACK = (80, 56, 214, 304)
RACK_X = (88, 206)                    # inner width of the rack units
UNIT_LEDS = [86, 100, 118, 140, 160, 192, 210, 226, 258]   # LED row of each unit
SCREEN = (466, 160, 568, 232)
PC = (430, 146, 610, 291)             # region that shakes
LED_GREEN = (34, 224, 34)
LED_OFF = (14, 74, 14)
CABLE = {(20, 169, 188), (191, 251, 255), (138, 232, 240), (255, 255, 255)}
CABLE_SHADOW = (11, 95, 106)
BREAK = (300, 334)                    # x range where the fiber gets cut
FONTS = "/usr/share/fonts/TTF/"
FONT = ImageFont.truetype(FONTS + "DejaVuSans.ttf", 19)
BOLD = ImageFont.truetype(FONTS + "DejaVuSans-Bold.ttf", 19)
MONO = ImageFont.truetype(FONTS + "DejaVuSansMono-Bold.ttf", 12)
BIG = ImageFont.truetype(FONTS + "DejaVuSansMono-Bold.ttf", 30)

base = Image.open(BASE).convert("RGB")
bpx = base.load()

# Where the action text starts, measured from the original line
rb = FONT.getbbox("Connected. Welcome to Dunne.systems!")
TX, TY = 36 - rb[0], 402 - rb[1]

leds = [(x, y) for x in range(80, 214) for y in range(56, 304) if bpx[x, y] == LED_GREEN]
cable_all = [(x, y) for x in range(214, 432) for y in range(196, 300)
             if bpx[x, y] in CABLE or bpx[x, y] == CABLE_SHADOW]
# Cable centerline ordered from the rack end to the PC end
cable_path = sorted({x: y for (x, y) in cable_all if bpx[x, y] in CABLE}.items())
CABLE_Y = dict(cable_path)


# --- shared drawing helpers --------------------------------------------------
def px2(d, x, y, col, w=2, h=2):
    """One 'art pixel' (2x2) snapped to the grid."""
    x, y = x - x % 2, y - y % 2
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=col)


def action(d, text, font=FONT, color=BLACK):
    d.rectangle((26, 392, 612, 438), fill=GRAY)
    d.text((TX, TY), text, font=font, fill=color)


def crt_text(d, big, small, show=True, color=(232, 232, 232)):
    """Black CRT with a big word and a small line under it."""
    x0, y0, x1, y1 = SCREEN
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(8, 8, 8))
    if not show:
        return
    w = BIG.getbbox(big)
    d.text(((x0 + x1 - (w[2] - w[0])) // 2 - w[0], y0 + 16 - w[1]), big, font=BIG, fill=color)
    m = MONO.getbbox(small)
    d.text(((x0 + x1 - (m[2] - m[0])) // 2 - m[0], y0 + 50), small, font=MONO, fill=color)


def crt_terminal(d, lines, cursor):
    """Green-on-black modem terminal on the CRT."""
    x0, y0, x1, y1 = SCREEN
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(8, 8, 8))
    for i, line in enumerate(lines[-4:]):
        d.text((x0 + 6, y0 + 6 + i * 15), line, font=MONO, fill=(80, 232, 96))
    if cursor:
        n = min(len(lines), 4)
        last = lines[-1] if lines else ""
        cx = x0 + 6 + int(MONO.getlength(last))
        d.rectangle((cx + 1, y0 + 8 + (n - 1) * 15, cx + 7, y0 + 18 + (n - 1) * 15), fill=(80, 232, 96))


def pulses(d, t, back=False, col=(255, 236, 140), x_range=None):
    n = len(cable_path)
    for k in range(3):
        i = (t * 9 + k * n // 3) % n
        if back:
            i = n - 1 - i
        x, y = cable_path[i]
        if x_range and not (x_range[0] <= x < x_range[1]):
            continue
        px2(d, x, y - 1, col, 4, 4)


def leds_set(px, colour_of):
    for (x, y) in leds:
        c = colour_of(x, y)
        if c:
            px[x, y] = c


def shake_pc(im, dx):
    x0, y0, x1, y1 = PC
    body = im.crop((x0, y0, x1, y1))
    ImageDraw.Draw(im).rectangle((x0, y0, x1 - 1, y1 - 1), fill=TEAL)
    im.paste(body, (x0 + dx, y0))


def cut_cable(px, d, t, sparks=True):
    for (x, y) in cable_all:
        if BREAK[0] <= x < BREAK[1]:
            px[x, y] = TEAL
    if sparks:
        rnd = random.Random(t)
        for _ in range(4):
            ex = rnd.choice([BREAK[0] - 2, BREAK[1]])
            ey = CABLE_Y.get(ex, 240)
            px2(d, ex + rnd.randint(-6, 6), ey + rnd.randint(-8, 4),
                rnd.choice([(255, 236, 140), (255, 250, 214), (246, 140, 24)]))


def bubble(d, t, frantic, text="?", at=(540, 76)):
    """Speech bubble above the monitor."""
    bob = (t % 2) * 2 if frantic else ((t // 2) % 2) * 2
    bx, by = at[0], at[1] - bob
    d.rectangle((bx, by, bx + 33, by + 33), fill=WHITE, outline=BLACK, width=2)
    d.polygon([(bx + 6, by + 33), (bx + 14, by + 33), (bx + 4, by + 44)], fill=WHITE, outline=BLACK)
    d.rectangle((bx + 6, by + 31, bx + 13, by + 33), fill=WHITE)
    q = BOLD.getbbox(text)
    d.text((bx + 17 - (q[2] - q[0]) // 2 - q[0], by + 7 - q[1]), text, font=BOLD, fill=RED if frantic else BLACK)
    if frantic:
        d.text((bx - 22, by + 14 + bob), "?", font=MONO, fill=WHITE)
        d.text((bx + 42, by + 4 - bob), "!", font=BOLD, fill=WHITE)


def clear_rack(im):
    """Remove the rack, keeping the floor shadow."""
    px = im.load()
    for x in range(RACK[0] - 2, RACK[2] + 2):
        for y in range(RACK[1] - 2, RACK[3] + 2):
            if px[x, y] not in (TEAL, SHADOW):
                px[x, y] = SHADOW if y > 290 else TEAL


def half_res_layer():
    """Transparent 320x230 canvas: art drawn here is scaled 2x so it lands
    on the same pixel grid as the rest of the scene."""
    lay = Image.new("RGBA", (320, 230), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)


def stamp(im, lay):
    im.paste(lay.resize((640, 460), Image.NEAREST), (0, 0), lay.resize((640, 460), Image.NEAREST))


# --- sprites -------------------------------------------------------------------
COLORS = {"O": (232, 140, 48), "W": (248, 240, 224), "P": (240, 140, 150), "K": (24, 20, 20),
          "B": (216, 212, 196), "L": (236, 232, 218), "S": (170, 164, 146), "G": (96, 92, 82)}
CORD = (150, 146, 130)


def outline(g):
    """Any clear cell touching the sprite becomes black."""
    H, W = len(g), len(g[0])
    filled = {(x, y) for y in range(H) for x in range(W) if g[y][x] != "."}
    for (x, y) in list(filled):
        for (nx, ny) in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in filled:
                g[ny][nx] = "K"
    return g


def grid(W, H):
    g = [["."] * W for _ in range(H)]

    def put(cells, c):
        for (x, y) in cells:
            if 0 <= x < W and 0 <= y < H:
                g[y][x] = c
    return g, put


def cat_sprite(step):
    """Plain orange cat running, facing right; step 0-3 is the run cycle."""
    g, put = grid(24, 14)
    put([(x, y) for x in range(6, 17) for y in range(5, 10)], "O")              # body
    put([(x, y) for x in range(16, 23) for y in range(2, 9)
         if (x, y) not in {(16, 2), (22, 2), (16, 8), (22, 8)}], "O")            # head
    put([(17, 0), (17, 1), (18, 1), (21, 0), (21, 1), (20, 1)], "O")             # ears
    put([(17, 1), (21, 1)], "P")                                                 # inner ears
    put([(20, 6), (21, 6), (22, 6), (19, 7), (20, 7), (21, 7)], "W")             # muzzle
    put([(22, 5)], "P")                                                          # nose
    put([(20, 4)], "K")                                                          # eye
    put([(5, 5), (4, 4), (3, 3), (3, 2), (2, 1), (2, 0)], "O")                   # tail, held up
    legs = [
        [(16, 10), (17, 11), (6, 10), (5, 11)],                                  # stretched
        [(15, 10), (15, 11), (7, 10), (7, 11)],
        [(13, 10), (12, 11), (9, 10), (10, 11)],                                 # tucked
        [(15, 10), (15, 11), (7, 10), (7, 11)],
    ][step % 4]
    put(legs, "O")
    put([legs[1], legs[3]], "W")                                                 # paws
    return outline(g)


def cat_sit(step, paw_up=False, chew=False):
    """Orange cat sitting, facing right. step swishes the tail."""
    g, put = grid(20, 19)
    put([(x, y) for x in range(2, 14) for y in range(9, 17)
         if ((x - 7.5) / 5.5) ** 2 + ((y - 13) / 4.2) ** 2 <= 1], "O")          # haunch
    put([(x, y) for x in range(9, 15) for y in range(7, 16)], "O")               # chest
    put([(x, y) for x in range(12, 15) for y in range(9, 14)], "W")              # white chest
    put([(x, y) for x in range(10, 18) for y in range(2, 9)
         if (x, y) not in {(10, 2), (17, 2), (10, 8), (17, 8)}], "O")            # head
    put([(11, 0), (11, 1), (12, 1), (16, 0), (16, 1), (15, 1)], "O")             # ears
    put([(11, 1), (16, 1)], "P")
    put([(15, 4)], "K")                                                          # eye
    put([(17, 5)], "P")                                                          # nose
    put([(15, 6), (16, 6), (17, 6), (14, 7), (15, 7), (16, 7)], "W")             # muzzle
    if chew:
        put([(17, 7)], "K")                                                      # mouth open
    if paw_up:
        put([(15, 10), (16, 9), (17, 8)], "O")                                   # paw reaching out
        put([(17, 8)], "W")
        put([(12, 14), (12, 15), (12, 16)], "O")
        put([(12, 16)], "W")
    else:
        put([(11, 14), (11, 15), (11, 16), (13, 14), (13, 15), (13, 16)], "O")   # front legs
        put([(11, 16), (13, 16)], "W")
    tail = [[(1, 16), (0, 15), (0, 14), (0, 13)], [(1, 16), (0, 16), (0, 15), (1, 14)]][step % 2]
    put(tail, "O")
    return outline(g)


def cat_loaf(step):
    """Orange cat asleep as a loaf, facing right."""
    g, put = grid(22, 10)
    put([(x, y) for x in range(1, 16) for y in range(3, 9)
         if ((x - 8) / 7.5) ** 2 + ((y - 8.5) / 5.5) ** 2 <= 1], "O")           # body
    put([(x, y) for x in range(12, 20) for y in range(2, 9)
         if (x, y) not in {(12, 2), (19, 2), (19, 8)}], "O")                     # head
    put([(13, 0), (13, 1), (14, 1), (18, 0), (18, 1), (17, 1)], "O")             # ears
    put([(13, 1), (18, 1)], "P")
    put([(15, 5), (16, 5)], "K")                                                 # closed eye
    put([(19, 6)], "P")
    put([(x, 8) for x in range(3, 12)], "O")
    put([(x, 9) for x in range(2, 9)] if step % 2 else [(x, 9) for x in range(2, 10)], "O")   # tail wrap
    return outline(g)


def mouse_sprite(step):
    """Beige two-button computer mouse on tiny legs, facing right."""
    g, put = grid(20, 13)
    put([(x, y) for x in range(2, 18) for y in range(1, 9)
         if ((x - 9.5) / 8) ** 2 + ((y - 9.5) / 8.5) ** 2 <= 1], "B")           # dome
    put([(x, y) for x in range(12, 18) for y in range(1, 9)
         if ((x - 9.5) / 8) ** 2 + ((y - 9.5) / 8.5) ** 2 <= 1], "L")           # buttons
    put([(12, y) for y in range(2, 9)], "G")                                     # seam: buttons | body
    put([(x, 2) for x in range(13, 17)], "G")                                    # groove between buttons
    put([(x, 9) for x in range(2, 18)], "S")                                     # base
    put([(14, 5), (15, 5), (14, 6), (15, 6)], "W")                               # big eye...
    put([(15, 6)], "K")                                                          # ...looking ahead
    put([(4, 10), (5, 11), (14, 10), (15, 11)] if step % 2 else
        [(6, 10), (6, 11), (12, 10), (12, 11)], "G")                             # scurrying legs
    return outline(g)


CATS = [cat_sprite(i) for i in range(4)]
MICE = [mouse_sprite(i) for i in range(2)]


def blit(layer, sprite, x, y, flip=False):
    w = len(sprite[0])
    for sy, row in enumerate(sprite):
        for sx, c in enumerate(row):
            if c != ".":
                layer[(x + (w - 1 - sx if flip else sx) * 2, y + sy * 2)] = COLORS[c]


def put_layer(im, layer, behind_only=True):
    """Draw sprite pixels; with behind_only they only cover the teal backdrop."""
    px = im.load()
    for (lx, ly), col in layer.items():
        for dx in (0, 1):
            for dy in (0, 1):
                X, Y = lx + dx, ly + dy
                if SCENE[0] <= X < SCENE[2] and SCENE[1] <= Y < SCENE[3] and \
                        (not behind_only or px[X, Y] in (TEAL, SHADOW)):
                    px[X, Y] = col


def with_chase(im, t, lap, mouse_leads=True, rightward=True, y=66):
    """The cat and the mouse run one lap every `lap` frames, behind the scene."""
    span = (SCENE[2] + 60) - (SCENE[0] - 180)
    p = (t % lap) * span // lap
    lead = SCENE[0] - 60 + p if rightward else SCENE[2] - p
    gap = 96 if rightward else -96
    mouse_x = lead if mouse_leads else lead - gap
    cat_x = lead - gap if mouse_leads else lead
    layer = {}
    my = y + 8 + (2 if t % 2 else 0)
    for i in range(0, 36, 2):                            # the cord flaps like a tail
        cx = mouse_x + (2 - i if rightward else 36 + i)
        cy = my + 12 + int(3 * math.sin(i / 5 + t * 1.3))
        layer[(cx - cx % 2, cy - cy % 2)] = CORD
    blit(layer, MICE[t % 2], mouse_x - mouse_x % 2, my, not rightward)
    blit(layer, CATS[t % 4], cat_x - cat_x % 2, y + (2 if t % 4 in (1, 2) else 0), not rightward)
    put_layer(im, layer)
    return im


def new_frame():
    im = base.copy()
    return im, im.load(), ImageDraw.Draw(im)


# --- 404: searching in a panic ------------------------------------------------------
def crt_search(d, t, fast=False):
    """A little file-list window on the CRT with a magnifier sweeping it."""
    x0, y0, x1, y1 = SCREEN
    d.rectangle((x0 + 10, y0 + 8, x1 - 11, y1 - 9), fill=WHITE)
    d.rectangle((x0 + 10, y0 + 8, x1 - 11, y0 + 15), fill=NAVY)
    for i in range(5):
        ry = y0 + 20 + i * 8
        d.rectangle((x0 + 16, ry, x0 + 21, ry + 3), fill=AMBER)          # folder icon
        d.rectangle((x0 + 26, ry + 1, x1 - 20 - (i * 9) % 24, ry + 2), fill=(128, 128, 128))
    span = (x1 - 11) - (x0 + 10) - 26
    k = (t * (4 if fast else 2)) % (2 * span // 6)
    mx = x0 + 14 + (k if k <= span // 6 else 2 * span // 6 - k) * 6
    my = y0 + 24 + ((t * 3) % 4) * (4 if fast else 2)
    d.ellipse((mx, my, mx + 13, my + 13), outline=BLACK, width=2)
    d.ellipse((mx + 3, my + 3, mx + 10, my + 10), fill=(200, 236, 255))
    d.line((mx + 12, my + 12, mx + 18, my + 18), fill=BLACK, width=3)


def sweat(d, t):
    for i, (sx, sy) in enumerate([(452, 150), (600, 158), (446, 176)]):
        y = sy + ((t + i * 2) % 4) * 4
        px2(d, sx, y, (191, 251, 255), 2, 4)
        px2(d, sx, y + 4, (138, 232, 240), 2, 2)


def scan_unit(d, px, u, t):
    y = UNIT_LEDS[u]
    d.rectangle((RACK_X[0] - 4, y - 9, RACK_X[1] + 4, y + 11), outline=AMBER, width=2)
    for (x, ly) in leds:
        if abs(ly - y) < 6:
            px[x, ly] = AMBER if t % 2 else LED_OFF


def f404(t, loop):
    im, px, d = new_frame()
    final = "Error 404: that page doesn't exist."
    if loop:
        crt_text(d, "404", "NOT FOUND", (t // 6) % 2 == 0)
        bubble(d, t // 3, False)
        action(d, final, color=RED)
        back = (t // 24) % 2 == 1                 # lap 2: the mouse chases the cat back
        return with_chase(im, t, 24, mouse_leads=not back, rightward=not back)
    shake = 0
    if t < 4:
        action(d, "Connected. Welcome to Dunne.systems!")
    elif t < 10:
        crt_search(d, t)
        pulses(d, t)
        action(d, "Looking for that page...")
    elif t < 22:
        u = min(len(UNIT_LEDS) - 1, (t - 10) * len(UNIT_LEDS) // 11)
        crt_search(d, t)
        scan_unit(d, px, u, t)
        pulses(d, t, back=t % 2 == 0)
        action(d, f"Searching rack A01: unit {u + 1} of {len(UNIT_LEDS)}...")
    elif t < 30:
        crt_search(d, t, fast=True)
        leds_set(px, lambda x, y: AMBER if (x // 6 + y // 10 + t) % 2 else LED_OFF)
        pulses(d, t * 2, back=t % 2 == 0)
        bubble(d, t, True)
        sweat(d, t)
        shake = 4 if t % 2 else -4
        action(d, "It was right here?!", font=BOLD)
    else:
        crt_text(d, "404", "NOT FOUND")
        bubble(d, t, False)
        action(d, final, color=RED)
    if shake:
        shake_pc(im, shake)
    return with_chase(im, t, 36)


# --- offline: no dial tone, the cat chewed the fiber -------------------------------
def cat_by_cut(im, t, chewing):
    """The culprit sits right of the gap, facing the cable end it chewed."""
    layer = {}
    x = BREAK[1] + 8
    y = CABLE_Y.get(BREAK[1] + 20, 250) - 38
    blit(layer, cat_sit(t // 2, chew=chewing and t % 2 == 0), x - x % 2, y - y % 2, flip=True)
    put_layer(im, layer)


def foffline(t, loop):
    im, px, d = new_frame()
    final = "Error: no dial tone. Check your connection."
    cut_cable(px, d, t, sparks=False)
    if loop:
        crt_terminal(d, ["ATDT 555-0404", "NO DIALTONE"], (t // 4) % 2 == 0)
        cat_by_cut(im, t, chewing=(t // 8) % 2 == 0)
        action(d, final, color=RED)
        return im
    attempt = min(3, t // 8 + 1)
    if t < 24:
        lines = []
        for a in range(1, attempt + 1):
            lines += ["ATDT 555-0404"] + (["NO CARRIER"] if a < attempt else [])
        crt_terminal(d, lines, t % 2 == 0)
        # the signal leaves the PC and dies at the gap
        pulses(d, t, back=True, x_range=(BREAK[1], 432))
        action(d, f"Dialing attempt {attempt} of 3...")
        cat_by_cut(im, t, chewing=True)
    else:
        crt_terminal(d, ["ATDT 555-0404", "NO DIALTONE"], True)
        bubble(d, t, False, "!", at=(540, 76)) if t < 28 else None
        action(d, final, color=RED)
        cat_by_cut(im, t, chewing=False)
    return im


# --- 403: locked out --------------------------------------------------------------------
def cage(im, t, wobble):
    lay, ld = half_res_layer()
    x0, y0, x1, y1 = RACK[0] // 2 - 2, RACK[1] // 2 - 1, RACK[2] // 2 + 1, RACK[3] // 2 - 6
    bar, edge = (168, 172, 178, 255), (24, 20, 20, 255)
    for x in range(x0, x1 + 1, 6):                                     # bars
        ld.line((x, y0, x, y1), fill=edge)
        ld.line((x + 1, y0, x + 1, y1), fill=bar)
    for y in (y0, (y0 + y1) // 2, y1):                                 # rails
        ld.rectangle((x0, y, x1 + 1, y + 1), fill=bar, outline=edge)
    lx, ly = (x0 + x1) // 2 - 6 + wobble, (y0 + y1) // 2 - 4           # padlock
    ld.arc((lx + 2, ly - 9, lx + 11, ly + 3), 180, 360, fill=edge, width=3)
    ld.arc((lx + 3, ly - 8, lx + 10, ly + 2), 180, 360, fill=bar, width=1)
    ld.rectangle((lx, ly, lx + 13, ly + 11), fill=(232, 184, 40, 255), outline=edge)
    ld.rectangle((lx + 6, ly + 3, lx + 7, ly + 7), fill=edge)
    stamp(im, lay)


def f403(t, loop):
    im, px, d = new_frame()
    final = "Error 403: you don't have access to rack A01."
    leds_set(px, lambda x, y: (232, 40, 24) if (t // 3) % 2 else LED_OFF)
    if loop:
        cage(im, t, (1 if t % 4 == 1 else -1 if t % 4 == 3 else 0))
        crt_text(d, "403", "ACCESS DENIED", (t // 6) % 2 == 0, color=(255, 96, 80))
        action(d, final, color=RED)
        cat_paw(im, t)
        return im
    cage(im, t, 0 if t < 14 else (2 if t % 2 else -2))
    if t < 4:
        action(d, "Connected. Welcome to Dunne.systems!")
    elif t < 14:
        pulses(d, t)
        action(d, "Requesting rack A01...")
    elif t < 22:
        pulses(d, t, back=True, col=(255, 96, 80))                     # bounced
        action(d, "Checking your badge...")
        crt_text(d, "...", "VERIFYING", (t // 2) % 2 == 0)
    else:
        crt_text(d, "403", "ACCESS DENIED", color=(255, 96, 80))
        action(d, final, color=RED)
    cat_paw(im, t)
    return im


def cat_paw(im, t):
    """The cat sits by the cage and swats at the lock."""
    layer = {}
    blit(layer, cat_sit(t // 2, paw_up=(t // 2) % 2 == 0), RACK[2] + 6, 248, flip=True)
    put_layer(im, layer)


# --- 500: on fire ---------------------------------------------------------------------
FIRE = [None, (70, 12, 8), (120, 20, 10), (176, 32, 12), (214, 60, 14), (236, 100, 18),
        (246, 140, 24), (252, 180, 40), (255, 212, 72), (255, 236, 140), (255, 250, 214)]
GX0, GY0 = (RACK[0] - 24) // 2, SCENE[1] // 2
GW, GH = (RACK[2] - RACK[0] + 48) // 2, (RACK[3] - SCENE[1] + 6) // 2
SLOTS = [100, 76, 112, 88, 64, 120, 52, 40]
TONGUE = [0.35 + 0.65 * abs(((i * 7) % 11) / 10 - 0.5) * 2 for i in range(GW)]
heat = [[0] * GW for _ in range(GH)]
fire_rnd = random.Random(500)


def step_fire(lit_n, intensity):
    """Doom-style fire: heat rises from the burning slots and cools."""
    for y in range(GH - 1):
        row, below = heat[y], heat[y + 1]
        for x in range(GW):
            h = below[x]
            nx = min(GW - 1, max(0, x + fire_rnd.randint(-1, 1)))
            row[nx] = max(0, h - (1 if fire_rnd.random() < 0.55 else 0)) if h else max(0, row[nx] - 1)
    rx0, rx1 = (RACK[0] // 2) - GX0 + 1, (RACK[2] // 2) - GX0 - 1
    for sy in SLOTS[:lit_n]:
        r = sy - GY0
        for x in range(rx0, rx1):
            heat[r][x] = (len(FIRE) - 1) if fire_rnd.random() < intensity * TONGUE[x] else max(heat[r][x] - 2, 0)


def draw_fire(d):
    for gy in range(GH):
        for gx in range(GW):
            h = heat[gy][gx]
            if h > 1:
                x, y = (GX0 + gx) * 2, (GY0 + gy) * 2
                if SCENE[0] <= x < SCENE[2] and SCENE[1] <= y < SCENE[3]:
                    d.rectangle((x, y, x + 1, y + 1), fill=FIRE[h])


def smoke(d, t):
    for i in range(min(18, max(0, t - 5) * 2)):
        age = (i * 9 + t * 4) % 72
        sx = RACK[0] + 24 + (i * 23) % 90 + age * 3
        sy = RACK[1] + 40 - age + (i % 3) * 6
        size = 6 + (age // 12) * 4
        col = [(58, 63, 70), (74, 80, 88), (96, 100, 106)][min(2, age // 24)]
        x0, y0 = max(SCENE[0], sx - sx % 2), max(SCENE[1], sy - sy % 2)
        x1, y1 = min(SCENE[2] - 1, x0 + size - 1), min(SCENE[3] - 1, y0 + size - 1)
        if x0 < x1 and y0 < y1:
            d.rectangle((x0, y0, x1, y1), fill=col)


def f500(t, loop):
    im, px, d = new_frame()
    final = "Error 500: Dunne.systems is on fire."
    if loop:
        leds_set(px, lambda x, y: (232, 40, 24) if t % 2 else LED_OFF)
        cut_cable(px, d, t)
        smoke(d, 40 + t)
        step_fire(len(SLOTS), 0.7)
        step_fire(len(SLOTS), 0.7)
        draw_fire(d)
        crt_text(d, "500", "NO CARRIER", (t // 4) % 2 == 0)
        action(d, final, color=RED)
        return with_chase(im, t * 2, 12, mouse_leads=True, y=286 - 30)
    if t >= 2:
        leds_set(px, lambda x, y: AMBER if t < 4 else ((232, 40, 24) if t % 2 else LED_OFF))
    if t >= 6:
        for (x, y) in cable_all:
            if bpx[x, y] in CABLE and fire_rnd.random() < 0.25:
                px[x, y] = fire_rnd.choice([(255, 212, 72), (255, 140, 24), (255, 250, 214)])
    if t >= 10:
        cut_cable(px, d, t)
    smoke(d, t * 2)
    if t >= 4:
        lit = max(0, min(len(SLOTS), (t - 4) + 1))
        step_fire(lit, 0.55)
        step_fire(lit, 0.55)
        draw_fire(d)
    if t < 2:
        action(d, "Connected. Welcome to Dunne.systems!")
    elif t < 5:
        crt_text(d, "!", "OVERHEAT", True, color=(255, 160, 64))
        action(d, "Warning: rack A01 is running hot...")
    elif t < 10:
        crt_text(d, "!!!", "OVERHEAT", t % 2 == 0, color=(255, 96, 80))
        action(d, final, color=RED)
    else:
        crt_text(d, "500", "NO CARRIER", True)
        action(d, final, color=RED)
    if t >= 6:
        return with_chase(im, t - 6, 12, mouse_leads=True, y=286 - 30)
    return im


# --- 503: down for maintenance ----------------------------------------------------------
def sign(im, drop, swing):
    lay, ld = half_res_layer()
    x0, x1 = RACK_X[0] // 2 - 2 + swing, RACK_X[1] // 2 + 2 + swing
    y0 = 74 - drop
    edge = (24, 20, 20, 255)
    ld.line((RACK[0] // 2 + 6, RACK[1] // 2 + 1, x0 + 4, y0), fill=edge)          # strings
    ld.line((RACK[2] // 2 - 6, RACK[1] // 2 + 1, x1 - 4, y0), fill=edge)
    ld.rectangle((x0, y0, x1, y0 + 20), fill=(240, 200, 40, 255), outline=edge)
    for i in range(x0 - 20, x1, 6):                                              # hazard stripes
        ld.line((max(x0 + 1, i), y0 + 1 + max(0, x0 + 1 - i), min(x1 - 1, i + 3), y0 + 4), fill=edge)
        ld.line((max(x0 + 1, i), y0 + 16 + max(0, x0 + 1 - i), min(x1 - 1, i + 3), y0 + 19), fill=edge)
    stamp(im, lay)
    d = ImageDraw.Draw(im)
    w = MONO.getbbox("MAINTENANCE")
    d.text(((x0 + x1) - (w[2] - w[0]) // 2 - w[0], (y0 + 10) * 2 - 7 - w[1] // 2), "MAINTENANCE",
           font=MONO, fill=(24, 20, 20))


def cat_nap(im, t):
    layer = {}
    blit(layer, cat_loaf(t // 4), 480, 130)
    put_layer(im, layer, behind_only=False)
    d = ImageDraw.Draw(im)
    for i, ch in enumerate("zZz"):
        k = (t + i * 4) % 12
        if k < 10:
            d.text((520 + i * 10 + k, 112 - k * 3 - i * 6), ch, font=MONO if i != 1 else BOLD, fill=WHITE)


def f503(t, loop):
    im, px, d = new_frame()
    final = "Error 503: rack A01 is down for maintenance."
    if loop:
        leds_set(px, lambda x, y: LED_OFF)
        sign(im, 0, (1 if t % 8 < 4 else -1))
        crt_text(d, "BRB", "BACK SOON", (t // 6) % 2 == 0)
        action(d, final, color=RED)
        cat_nap(im, t)
        return im
    n_off = max(0, min(len(UNIT_LEDS), t - 5))                # one unit goes dark per frame
    dark = set(UNIT_LEDS[:n_off])
    leds_set(px, lambda x, y: LED_OFF if any(abs(y - u) < 6 for u in dark) else None)
    if t < 4:
        action(d, "Connected. Welcome to Dunne.systems!")
    elif t < 15:
        action(d, f"Scheduled maintenance in {max(1, 3 - (t - 4) // 4)}...")
    else:
        drop = max(0, [140, 90, 40, 0, -6, 0][min(5, t - 15)])
        sign(im, drop, 0)
        crt_text(d, "BRB", "BACK SOON")
        action(d, final, color=RED)
    if t >= 20:
        cat_nap(im, t)
    return im


# --- 418: I'm a teapot ------------------------------------------------------------------
def teapot(im, t, morph=1.0):
    clear_rack(im)
    lay, ld = half_res_layer()
    cx, cy = (RACK[0] + RACK[2]) // 4, 112
    s = morph
    edge, porcelain, blue = (24, 20, 20, 255), (240, 240, 232, 255), (44, 124, 216, 255)
    rx, ry = int(34 * s), int(28 * s)
    sp = cable_path[0]                                                    # spout meets the fiber
    ld.polygon([(cx + rx - 6, cy - 2), (cx + rx - 4, cy + 12), (sp[0] // 2 - 1, sp[1] // 2 + 1),
                (sp[0] // 2 + 1, sp[1] // 2 - 4)], fill=porcelain, outline=edge)       # spout
    ld.arc((cx - rx - 12, cy - 13, cx - rx + 14, cy + 13), 90, 270, fill=edge, width=5)  # handle
    ld.arc((cx - rx - 10, cy - 11, cx - rx + 12, cy + 11), 90, 270, fill=porcelain, width=2)
    ld.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=porcelain, outline=edge)       # body
    ld.rectangle((cx - rx + 4, cy - 3, cx + rx - 4, cy + 3), fill=blue)                 # blue band
    for k in range(-2, 3):
        ld.ellipse((cx + k * 12 - 2, cy - 9, cx + k * 12 + 2, cy - 5), fill=blue)
    ld.ellipse((cx - 16, cy - ry - 5, cx + 16, cy - ry + 5), fill=porcelain, outline=edge)  # lid
    ld.ellipse((cx - 3, cy - ry - 10, cx + 3, cy - ry - 4), fill=blue, outline=edge)        # knob
    stamp(im, lay)
    if morph >= 1:                                                        # steam
        d = ImageDraw.Draw(im)
        for i in range(3):
            k = (t + i * 3) % 9
            x = sp[0] - 8 + int(4 * math.sin((t + i * 5) / 2)) - k
            y = sp[1] - 24 - k * 5
            if y > SCENE[1]:
                d.rectangle((x - x % 2, y - y % 2, x - x % 2 + 5, y - y % 2 + 5), fill=(232, 240, 240))


def cat_tea(im, t):
    layer = {}
    blit(layer, cat_sit(t // 3), RACK[2] + 30, 262, flip=True)
    put_layer(im, layer)


def f418(t, loop):
    im, px, d = new_frame()
    final = "Error 418: I'm a teapot. I can't brew coffee."
    if loop:
        teapot(im, t)
        crt_text(d, "418", "I'M A TEAPOT", (t // 6) % 2 == 0)
        action(d, final, color=RED)
        cat_tea(im, t)
        return im
    if t < 4:
        action(d, "Connected. Welcome to Dunne.systems!")
    elif t < 12:
        pulses(d, t)
        crt_text(d, "BREW", "COFFEE...", (t // 2) % 2 == 0, color=(232, 184, 120))
        action(d, "Brewing coffee on rack A01...")
    elif t < 16:
        if t % 2 == 0:                                                    # flicker as it changes
            teapot(im, t, morph=0.6 + (t - 12) * 0.1)
        crt_text(d, "???", "", True)
        action(d, "Hang on, something's wrong...")
    else:
        teapot(im, t)
        crt_text(d, "418", "I'M A TEAPOT")
        action(d, final, color=RED)
    if t >= 16:
        cat_tea(im, t)
    return im


# --- build ---------------------------------------------------------------------------
SCREENS = {
    # name: (frame fn, frames once, ms once, frames loop, ms loop, still = loop frame)
    "404": (f404, 36, 100, 48, 100, 9),
    "offline": (foffline, 32, 100, 16, 120, 0),
    "403": (f403, 30, 100, 12, 120, 2),
    "500": (f500, 18, 160, 6, 160, 3),
    "503": (f503, 28, 100, 16, 150, 0),
    "418": (f418, 26, 100, 12, 150, 0),
}

for name, (fn, n1, ms1, n2, ms2, still) in SCREENS.items():
    if ONLY and name not in ONLY:
        continue
    random.seed(name)
    heat = [[0] * GW for _ in range(GH)] if name == "500" else heat
    once = [fn(t, False) for t in range(n1)]
    loop = [fn(t, True) for t in range(n2)]
    picks = once[:: max(1, n1 // 5)] + [loop[still]]
    sheet = Image.new("RGB", (640, 460 * len(picks)))
    for i, f in enumerate(picks):
        sheet.paste(f, (0, 460 * i))
    pal = sheet.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    def q(f):
        return f.quantize(palette=pal, dither=Image.Dither.NONE)

    qo = [q(f) for f in once]
    qo[0].save(f"{OUT}/dialing-{name}.gif", save_all=True, append_images=qo[1:], duration=ms1, optimize=True)
    ql = [q(f) for f in loop]
    ql[0].save(f"{OUT}/dialing-{name}-loop.gif", save_all=True, append_images=ql[1:], duration=ms2,
               loop=0, optimize=True)
    q(loop[still]).save(f"{OUT}/dialing-{name}-end.png", optimize=True)
    print(f"{name}: once {n1}x{ms1}ms = {n1 * ms1}ms, loop {n2}x{ms2}ms")
