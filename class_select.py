# class_select.py
# Pixel Adventures — Class Selection Screen (after Title)
# Larger, more detailed pixel sprites (24x24) with subtle bobbing for selection.

import pygame
import math
import random

TITLE = "Choose Your Class"
ICON_SIZE = 24  # bigger canvas for more detail

# 3 FF-inspired classes with visible gameplay effects in the demo
CLASSES = [
    {
        "id": "knight",
        "name": "Knight",
        "color": (220, 70, 70),
        "desc": "Frontline stalwart with heavy armor and steady offense.",
        "bonuses": [
            "+40% Max HP",
            "+25% Melee ATK",
            "-10% Move Speed",
            "Faster Special charge"
        ],
        "stats": {
            "hp": 14, "mp": 6, "atk": 3, "mag": 0,
            "spd_mult": 0.90,        # affects movement speed
            "magnet": 10,            # coin pull radius (pixels in virtual space)
            "special_rate": 1.25     # HUD bar fill
        }
    },
    {
        "id": "black_mage",
        "name": "Black Mage",
        "color": (90, 160, 255),
        "desc": "Glass cannon. Focused arcane damage and MP economy.",
        "bonuses": [
            "+50% MP",
            "+35% Magic Power",
            "Normal Move Speed",
            "Special builds on coin pick-ups"
        ],
        "stats": {
            "hp": 9, "mp": 12, "atk": 0, "mag": 3,
            "spd_mult": 1.00,
            "magnet": 14,
            "special_rate": 1.00
        }
    },
    {
        "id": "white_mage",
        "name": "White Mage",
        "color": (250, 230, 120),
        "desc": "Support caster. Durable enough with wide utility.",
        "bonuses": [
            "+20% Max HP",
            "+25% Healing/Support",
            "-5% Move Speed",
            "Wider pickup radius"
        ],
        "stats": {
            "hp": 12, "mp": 10, "atk": 1, "mag": 2,
            "spd_mult": 0.95,
            "magnet": 18,
            "special_rate": 0.9
        }
    },
]

# ───────────────────────── helpers ─────────────────────────

def _make_text(text, size, color, shadow=True):
    font = pygame.font.Font(None, size)
    surf = font.render(text, False, color)
    if not shadow:
        return surf
    sh = font.render(text, False, (0, 0, 0))
    out = pygame.Surface((surf.get_width()+1, surf.get_height()+1), pygame.SRCALPHA)
    out.blit(sh, (1, 1))
    out.blit(surf, (0, 0))
    return out

def _darker(c, amt=30):
    return (max(0, c[0]-amt), max(0, c[1]-amt), max(0, c[2]-amt))

def _lighter(c, amt=30):
    return (min(255, c[0]+amt), min(255, c[1]+amt), min(255, c[2]+amt))

def _dither_rect(surf, rect, c1, c2):
    """Simple 2-color dithering fill for tiny pixel shading."""
    x0, y0, w, h = rect
    for y in range(y0, y0+h):
        for x in range(x0, x0+w):
            surf.set_at((x, y), c1 if ((x + y) & 1) == 0 else c2)

def _class_icon(cid, accent):
    """
    Return a detailed 24x24 icon surface.
    We draw into a 22x22 'inner' canvas with a 1px border for crisp framing.
    """
    border_col = (20, 20, 34)
    panel_col = (14, 14, 24)

    s = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
    # frame
    pygame.draw.rect(s, border_col, (0, 0, ICON_SIZE, ICON_SIZE))
    inner = pygame.Surface((ICON_SIZE-2, ICON_SIZE-2), pygame.SRCALPHA)
    inner.fill(panel_col)

    # shared palette bits
    steel = (170, 175, 195)
    steel_dark = (110, 115, 140)
    steel_light = (220, 225, 240)

    gold = (210, 180, 60)
    wood = (120, 80, 40)

    linen = (240, 240, 240)
    linen_shade = (210, 210, 210)

    night = (10, 10, 14)
    shadow = (0, 0, 0)

    # tiny sparkle helper
    def sparkle(x, y, col):
        inner.set_at((x, y), col)
        if 1 <= x < inner.get_width()-1 and 1 <= y < inner.get_height()-1:
            inner.set_at((x+1, y), _lighter(col, 25))
            inner.set_at((x, y+1), _lighter(col, 25))

    if cid == "knight":
        # — Helmet (crest plume uses accent) —
        # Crest
        pygame.draw.polygon(inner, accent, [(11, 2), (16, 4), (14, 1)])
        pygame.draw.line(inner, _darker(accent, 40), (12, 3), (15, 4))
        # Helm dome
        pygame.draw.rect(inner, steel, (6, 3, 10, 5))
        pygame.draw.rect(inner, steel_dark, (6, 3, 10, 5), 1)
        # Visor slit
        pygame.draw.rect(inner, shadow, (8, 5, 6, 1))
        pygame.draw.rect(inner, steel_light, (7, 4, 1, 1))
        # Cheek guards
        pygame.draw.rect(inner, steel, (5, 6, 3, 3))
        pygame.draw.rect(inner, steel, (14, 6, 3, 3))
        # Face hint (peach highlight)
        pygame.draw.rect(inner, (255, 220, 180), (9, 6, 4, 2))

        # — Pauldrons & Chestplate —
        pygame.draw.rect(inner, steel, (4, 9, 14, 6))
        pygame.draw.rect(inner, steel_dark, (4, 9, 14, 6), 1)
        _dither_rect(inner, (5, 10, 12, 4), steel, steel_light)
        # Rivets
        for x in (6, 10, 14):
            inner.set_at((x, 11), steel_light)

        # Emblem on chest (accent)
        pygame.draw.rect(inner, accent, (10, 11, 2, 2))
        inner.set_at((11, 11), _lighter(accent, 30))

        # — Shield (left) with crest —
        pygame.draw.rect(inner, steel_dark, (2, 11, 3, 7))
        pygame.draw.rect(inner, steel, (3, 12, 1, 5))
        pygame.draw.rect(inner, gold, (3, 13, 1, 1))  # crest dot

        # — Sword (right) —
        pygame.draw.rect(inner, wood, (18, 13, 2, 2))         # hilt
        pygame.draw.rect(inner, gold, (17, 12, 4, 1))         # guard
        pygame.draw.rect(inner, steel_light, (19, 6, 1, 7))   # blade
        pygame.draw.rect(inner, steel, (18, 7, 1, 5))
        sparkle(19, 7, steel_light)

        # — Greaves —
        pygame.draw.rect(inner, steel_dark, (8, 15, 2, 4))
        pygame.draw.rect(inner, steel_dark, (12, 15, 2, 4))
        pygame.draw.rect(inner, steel_light, (8, 16, 1, 1))
        pygame.draw.rect(inner, steel_light, (12, 16, 1, 1))

    elif cid == "black_mage":
        # — Wizard Hat —
        hat = (40, 40, 70)
        hat_shade = (30, 30, 55)
        band = accent
        # brim
        pygame.draw.rect(inner, hat, (5, 8, 12, 2))
        # cone
        pygame.draw.polygon(inner, hat, [(8, 8), (15, 8), (12, 1)])
        pygame.draw.polygon(inner, hat_shade, [(12, 1), (15, 8), (13, 8)])  # side shade
        # band
        pygame.draw.rect(inner, band, (8, 9, 7, 1))

        # — Shadowed face with glowing eyes —
        face = (18, 18, 22)
        pygame.draw.rect(inner, face, (9, 10, 6, 4))
        eye = (255, 248, 110)
        inner.set_at((10, 12), eye)
        inner.set_at((13, 12), eye)
        sparkle(10, 12, (255, 255, 180))
        sparkle(13, 12, (255, 255, 180))

        # — Robe with trim —
        robe = (5, 5, 8)
        trim = _lighter(accent, 20)
        pygame.draw.rect(inner, robe, (7, 14, 10, 6))
        _dither_rect(inner, (8, 15, 8, 4), robe, (10, 10, 16))
        pygame.draw.rect(inner, trim, (7, 19, 10, 1))   # hem
        pygame.draw.rect(inner, trim, (11, 14, 2, 5))   # front trim

        # — Staff with ember —
        shaft = (120, 80, 40)
        ember = (255, 120, 60)
        pygame.draw.rect(inner, shaft, (3, 6, 1, 12))
        pygame.draw.rect(inner, ember, (3, 5, 1, 1))
        sparkle(3, 5, (255, 200, 120))

        # Boots
        pygame.draw.rect(inner, (40, 40, 70), (9, 20, 2, 2))
        pygame.draw.rect(inner, (40, 40, 70), (13, 20, 2, 2))

    elif cid == "white_mage":
        # — Hood & Robe —
        hood = linen
        hood_edge = _darker(linen, 40)
        pygame.draw.rect(inner, hood, (7, 2, 10, 7))
        pygame.draw.rect(inner, hood_edge, (7, 2, 10, 7), 1)

        # face & eyes
        skin = (255, 220, 190)
        pygame.draw.rect(inner, skin, (10, 5, 4, 2))
        inner.set_at((11, 6), (0, 0, 0))
        inner.set_at((12, 6), (0, 0, 0))

        # robe body
        pygame.draw.rect(inner, linen, (6, 9, 12, 10))
        _dither_rect(inner, (7, 10, 10, 7), linen, linen_shade)
        pygame.draw.rect(inner, hood_edge, (6, 9, 12, 10), 1)

        # classic red triangular trim at hem
        red = (200, 50, 50)
        for i in range(6):
            x = 6 + i*2
            pygame.draw.polygon(inner, red, [(x, 19), (x+1, 17), (x+2, 19)])

        # staff with green focus
        staff = (40, 160, 60)
        pygame.draw.rect(inner, (120, 80, 40), (17, 6, 1, 12))
        pygame.draw.rect(inner, staff, (17, 5, 1, 1))
        sparkle(17, 5, (170, 255, 170))

        # sleeves / hands hint
        pygame.draw.rect(inner, hood_edge, (6, 12, 3, 2))
        pygame.draw.rect(inner, hood_edge, (15, 12, 3, 2))
        pygame.draw.rect(inner, skin, (8, 13, 1, 1))
        pygame.draw.rect(inner, skin, (15, 13, 1, 1))

        # shoes
        pygame.draw.rect(inner, (50, 50, 70), (9, 20, 2, 2))
        pygame.draw.rect(inner, (50, 50, 70), (13, 20, 2, 2))

    else:
        # fallback
        pygame.draw.rect(inner, accent, (1, 1, inner.get_width()-2, inner.get_height()-2))

    s.blit(inner, (1, 1))
    return s

# ───────────────────────── screen ─────────────────────────

def run(screen, clock, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    # Prebuild icons/text
    base_icons = [_class_icon(c["id"], c["color"]) for c in CLASSES]
    title = _make_text(TITLE, 20, (255, 230, 140))
    prompt = _make_text("← →  Select   Z/ENTER  Confirm   ESC  Back", 12, (230, 230, 230), shadow=False)

    # Animated background dots
    dots = [{"x": random.randrange(0, vw), "y": random.randrange(0, vh), "s": random.choice([1, 1, 2])} for _ in range(60)]
    t = 0.0
    idx = 0

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return "back"
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    idx = (idx - 1) % len(CLASSES)
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    idx = (idx + 1) % len(CLASSES)
                if e.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    chosen = dict(CLASSES[idx])
                    chosen["stats"] = dict(chosen["stats"])
                    return chosen

        # update dots
        for d in dots:
            d["y"] += d["s"] * dt * 20
            if d["y"] > vh:
                d["y"] = -2
                d["x"] = random.randrange(0, vw)

        # draw bg
        surf.fill((12, 12, 20))
        for d in dots:
            surf.set_at((int(d["x"]), int(d["y"])), (60, 60, 90))

        # header
        ty = 8 + int(math.sin(t * 2.0) * 1)
        surf.blit(title, ((vw - title.get_width()) // 2, ty))

        # three columns
        col_w = vw // 3
        for i, c in enumerate(CLASSES):
            cx = i * col_w
            # card background
            pygame.draw.rect(surf, (22, 22, 36), (cx + 4, 28, col_w - 8, vh - 36))
            pygame.draw.rect(surf, (40, 40, 70), (cx + 4, 28, col_w_
