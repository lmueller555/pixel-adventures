# class_select.py
# Pixel Adventures — Class Selection Screen (after Title)
# Taller, more detailed pixel sprites (24x36) with subtle bobbing for selection.

import pygame
import math
import random

TITLE = "Choose Your Class"
ICON_W, ICON_H = 24, 36  # wider/taller canvas for more detail

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

def _class_icon(cid, accent, with_panel=True, frame=0):
    """Return a detailed class sprite surface (24x36).
    If `with_panel` is True a dark backdrop and border are drawn (for selection cards).
    If False, a transparent sprite is returned (for in-world use). `frame` selects
    a simple 2-frame walk pose (0 or 1).
    """
    border_col = (20, 20, 34)
    panel_col  = (14, 14, 24)

    s = pygame.Surface((ICON_W, ICON_H), pygame.SRCALPHA)
    if with_panel:
        pygame.draw.rect(s, border_col, (0, 0, ICON_W, ICON_H))
        inner = pygame.Surface((ICON_W - 2, ICON_H - 2), pygame.SRCALPHA)
        inner.fill(panel_col)
        blit_target, blit_pos = s, (1, 1)
    else:
        inner = pygame.Surface((ICON_W - 2, ICON_H - 2), pygame.SRCALPHA)
        blit_target, blit_pos = None, (0, 0)

    iw, ih = inner.get_width(), inner.get_height()

    # shared palette bits
    steel       = (170, 175, 195)
    steel_dark  = (110, 115, 140)
    steel_light = (220, 225, 240)

    gold  = (210, 180, 60)
    wood  = (120, 80, 40)

    linen       = (240, 240, 240)
    linen_shade = (210, 210, 210)

    night  = (10, 10, 14)
    shadow = (0, 0, 0)

    # tiny sparkle helper
    def sparkle(x, y, col):
        if 0 <= x < iw and 0 <= y < ih:
            inner.set_at((x, y), col)
        if 1 <= x < iw-1 and 1 <= y < ih-1:
            inner.set_at((x+1, y), _lighter(col, 25))
            inner.set_at((x, y+1), _lighter(col, 25))

    if cid == "knight":
        # ── Helmet & Crest ──
        pygame.draw.polygon(inner, accent, [(iw//2 - 1, 2), (iw//2 + 4, 5), (iw//2 + 2, 1)])
        pygame.draw.line(inner, _darker(accent, 40), (iw//2, 4), (iw//2 + 3, 5))
        pygame.draw.rect(inner, steel,      (iw//2 - 5, 4, 10, 6))   # helm dome
        pygame.draw.rect(inner, steel_dark, (iw//2 - 5, 4, 10, 6), 1)
        pygame.draw.rect(inner, shadow,     (iw//2 - 3, 6, 6, 1))    # visor slit
        pygame.draw.rect(inner, steel_light,(iw//2 - 4, 5, 1, 1))
        pygame.draw.rect(inner, steel, (iw//2 - 6, 7, 3, 3))         # cheek guards
        pygame.draw.rect(inner, steel, (iw//2 + 3, 7, 3, 3))
        pygame.draw.rect(inner, (255, 220, 180), (iw//2 - 2, 7, 4, 2))  # face hint

        # ── Pauldrons & Chestplate ── (shifted down for taller body)
        pygame.draw.rect(inner, steel,      (iw//2 - 8, 12, 16, 7))
        pygame.draw.rect(inner, steel_dark, (iw//2 - 8, 12, 16, 7), 1)
        _dither_rect(inner, (iw//2 - 7, 13, 14, 5), steel, steel_light)
        for x in (iw//2 - 6, iw//2 - 1, iw//2 + 4):
            inner.set_at((x, 14), steel_light)

        # Emblem
        pygame.draw.rect(inner, accent, (iw//2 - 1, 15, 2, 2))
        inner.set_at((iw//2, 15), _lighter(accent, 30))

        # ── Shield (left) ──
        pygame.draw.rect(inner, steel_dark, (2, 16, 4, 9))
        pygame.draw.rect(inner, steel,      (3, 17, 2, 7))
        pygame.draw.rect(inner, gold,       (3, 19, 2, 1))

        # ── Sword (right) extended ──
        pygame.draw.rect(inner, wood,        (iw - 6, 18, 3, 2))   # hilt
        pygame.draw.rect(inner, gold,        (iw - 7, 17, 5, 1))   # guard
        pygame.draw.rect(inner, steel_light, (iw - 5, 7, 1, 11))   # upper blade
        pygame.draw.rect(inner, steel,       (iw - 6, 9, 1, 9))
        pygame.draw.rect(inner, steel_light, (iw - 5, 7+11, 1, 6)) # lower blade
        sparkle(iw - 5, 9, steel_light)

        # ── Belt & Tassets ──
        pygame.draw.rect(inner, _darker(wood, 15), (iw//2 - 7, 19, 14, 1))
        pygame.draw.rect(inner, gold, (iw//2 - 1, 19, 2, 1))
        pygame.draw.rect(inner, steel, (iw//2 - 6, 20, 12, 3))

        # ── Greaves / Boots (use simple 2-frame walk) ──
        ly, ry = (24, 26) if (frame % 2) else (26, 24)
        pygame.draw.rect(inner, steel_dark, (iw//2 - 3, ly, 3, 6))
        pygame.draw.rect(inner, steel_dark, (iw//2 + 1, ry, 3, 6))
        pygame.draw.rect(inner, steel_light, (iw//2 - 3, ly+1, 1, 1))
        pygame.draw.rect(inner, steel_light, (iw//2 + 1, ry+1, 1, 1))
        # soles
        pygame.draw.rect(inner, (40, 40, 60), (iw//2 - 3, ly+5, 3, 1))
        pygame.draw.rect(inner, (40, 40, 60), (iw//2 + 1, ry+5, 3, 1))

        # ── Cape tail (accent shade) ──
        cape = _darker(accent, 35)
        pygame.draw.polygon(inner, cape, [(iw//2 - 8, 13), (iw//2 - 3, 21), (iw//2 - 8, 28)])

    elif cid == "black_mage":
        # ── Hat ──
        hat = (40, 40, 70)
        hat_shade = (30, 30, 55)
        band = accent
        pygame.draw.rect(inner, hat, (5, 10, 12, 2))  # brim (lowered)
        pygame.draw.polygon(inner, hat, [(8, 10), (15, 10), (12, 2)])  # cone
        pygame.draw.polygon(inner, hat_shade, [(12, 2), (15, 10), (13, 10)])
        pygame.draw.rect(inner, band, (8, 11, 7, 1))

        # ── Shadowed face with glowing eyes ──
        face = (18, 18, 22)
        pygame.draw.rect(inner, face, (9, 12, 6, 4))
        eye = (255, 248, 110)
        inner.set_at((10, 14), eye)
        inner.set_at((13, 14), eye)
        sparkle(10, 14, (255, 255, 180))
        sparkle(13, 14, (255, 255, 180))

        # ── Robe with deeper body & trim ──
        robe = (5, 5, 8)
        trim = _lighter(accent, 20)
        pygame.draw.rect(inner, robe, (7, 18, 10, 10))
        _dither_rect(inner, (8, 19, 8, 8), robe, (10, 10, 16))
        pygame.draw.rect(inner, trim, (7, 27, 10, 1))   # hem
        pygame.draw.rect(inner, trim, (11, 18, 2, 8))   # front trim

        # ── Staff with ember (longer) ──
        shaft = (120, 80, 40)
        ember = (255, 120, 60)
        pygame.draw.rect(inner, shaft, (3, 8, 1, 18))
        pygame.draw.rect(inner, ember, (3, 7, 1, 1))
        sparkle(3, 7, (255, 200, 120))

        # ── Boots (2-frame) ──
        boot = (40, 40, 70)
        if frame % 2 == 0:
            lx, rx = 9, 13
        else:
            lx, rx = 8, 14
        pygame.draw.rect(inner, boot, (lx, 30, 2, 2))
        pygame.draw.rect(inner, boot, (rx, 30, 2, 2))

        # trailing robe flare
        pygame.draw.polygon(inner, (8, 8, 12), [(7, 26), (6, 30), (9, 28)])

    elif cid == "white_mage":
        # ── Hood & Robe ──
        hood = linen
        hood_edge = _darker(linen, 40)
        pygame.draw.rect(inner, hood, (7, 4, 10, 7))
        pygame.draw.rect(inner, hood_edge, (7, 4, 10, 7), 1)

        # face & eyes
        skin = (255, 220, 190)
        pygame.draw.rect(inner, skin, (10, 7, 4, 2))
        inner.set_at((11, 8), (0, 0, 0))
        inner.set_at((12, 8), (0, 0, 0))

        # robe body (taller with dithering)
        pygame.draw.rect(inner, linen, (6, 14, 12, 12))
        _dither_rect(inner, (7, 15, 10, 10), linen, linen_shade)
        pygame.draw.rect(inner, hood_edge, (6, 14, 12, 12), 1)

        # classic red triangular trim at lower hem (shifted down)
        red = (200, 50, 50)
        base_y = 26
        for i in range(6):
            x = 6 + i*2
            pygame.draw.polygon(inner, red, [(x, base_y), (x+1, base_y-2), (x+2, base_y)])

        # sleeves / hands hint
        pygame.draw.rect(inner, hood_edge, (6, 18, 3, 2))
        pygame.draw.rect(inner, hood_edge, (15, 18, 3, 2))
        pygame.draw.rect(inner, skin, (8, 19, 1, 1))
        pygame.draw.rect(inner, skin, (15, 19, 1, 1))

        # staff with green focus (longer)
        staff = (40, 160, 60)
        pygame.draw.rect(inner, (120, 80, 40), (iw - 7, 8, 1, 18))
        pygame.draw.rect(inner, staff, (iw - 7, 7, 1, 1))
        sparkle(iw - 7, 7, (170, 255, 170))

        # shoes (2-frame) lower
        shoe = (50, 50, 70)
        if frame % 2 == 0:
            lx, rx = 9, 13
        else:
            lx, rx = 8, 14
        pygame.draw.rect(inner, shoe, (lx, 30, 2, 2))
        pygame.draw.rect(inner, shoe, (rx, 30, 2, 2))

        # outer hem highlight
        pygame.draw.line(inner, _lighter(linen, 20), (6, 25), (17, 25))

    else:
        # fallback
        pygame.draw.rect(inner, accent, (1, 1, iw-2, ih-2))

    if blit_target:
        blit_target.blit(inner, blit_pos)
        return s
    return inner

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

    # Card layout constants (relative so taller icons fit cleanly)
    card_top = 28
    card_bottom_margin = 36  # space for prompt/footer
    card_h = vh - card_top - card_bottom_margin
    icon_top_margin = 6
    name_gap = 2
    sep_gap = 6
    bonuses_gap = 6

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
            pygame.draw.rect(surf, (22, 22, 36), (cx + 4, card_top, col_w - 8, card_h))
            pygame.draw.rect(surf, (40, 40, 70), (cx + 4, card_top, col_w - 8, card_h), 1)

            # icon + name
            ic = base_icons[i]
            # subtle bob for selected class
            bob = -1 if i == idx else 0
            oy = card_top + icon_top_margin + bob + (int(math.sin(t * 3.0)) if i == idx else 0)
            surf.blit(ic, (cx + (col_w - ic.get_width()) // 2, oy))

            nm = _make_text(c["name"], 16, c["color"])
            name_y = oy + ICON_H + name_gap
            surf.blit(nm, (cx + (col_w - nm.get_width()) // 2, name_y))

            # small separator under name
            sep_y = name_y + nm.get_height() + sep_gap
            pygame.draw.line(surf, (50, 50, 90), (cx + 10, sep_y), (cx + col_w - 10, sep_y))

            # bonuses text
            y = sep_y + bonuses_gap
            bonus_color = (230, 230, 230) if i != idx else (255, 255, 180)
            for b in c["bonuses"]:
                line = _make_text(b, 12, bonus_color, shadow=False)
                if line.get_width() <= col_w - 16:
                    if y + 12 <= card_top + card_h - 4:
                        surf.blit(line, (cx + 8, y))
                    y += 12
                else:
                    # crude wrap
                    mid = len(b) // 2
                    cut = b[:mid].rstrip() + "-"
                    line1 = _make_text(cut, 12, bonus_color, shadow=False)
                    line2 = _make_text(b[mid:].lstrip(), 12, bonus_color, shadow=False)
                    if y + 12 <= card_top + card_h - 4:
                        surf.blit(line1, (cx + 8, y))
                    y += 12
                    if y + 12 <= card_top + card_h - 4:
                        surf.blit(line2, (cx + 8, y))
                    y += 12

            # selection highlight
            if i == idx:
                pygame.draw.rect(surf, c["color"], (cx + 6, card_top + 2, col_w - 12, card_h - 4), 1)

        # prompt (blinking)
        if int(t * 2) % 2 == 0:
            surf.blit(prompt, ((vw - prompt.get_width()) // 2, vh - 16))

        # scale to window (nearest-neighbor)
        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()
