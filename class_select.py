# class_select.py
# Pixel Adventures — Class Selection Screen (after Title)
# Uses the same low-res virtual canvas scaled to fill the screen.

import pygame
import math
import random

TITLE = "Choose Your Class"

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

def _class_icon(cid, color):
    """Return a 12x12 icon with simple facial and armor detail."""
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.rect(s, (25, 25, 45), (0, 0, 12, 12))  # border
    inner = pygame.Surface((10, 10), pygame.SRCALPHA)

    if cid == "knight":
        outline = (30, 30, 70)
        armor = (170, 170, 190)
        face = (255, 220, 180)
        eyes = (255, 255, 255)
        blade = (210, 210, 220)
        hilt = (120, 80, 40)
        shield = (160, 130, 70)

        # Helmet and body
        pygame.draw.rect(inner, armor, (2, 0, 6, 3))
        pygame.draw.rect(inner, armor, (2, 4, 6, 6))
        pygame.draw.rect(inner, outline, (2, 0, 6, 3), 1)
        pygame.draw.rect(inner, outline, (2, 4, 6, 6), 1)

        # Face
        pygame.draw.rect(inner, face, (3, 1, 4, 2))
        inner.set_at((4, 2), eyes)
        inner.set_at((5, 2), eyes)

        # Shield and sword
        pygame.draw.rect(inner, outline, (0, 4, 2, 4))
        pygame.draw.rect(inner, shield, (1, 5, 1, 2))
        pygame.draw.rect(inner, color, (1, 5, 1, 2), 1)
        pygame.draw.rect(inner, blade, (8, 1, 1, 7))
        pygame.draw.rect(inner, hilt, (7, 6, 3, 2))

        # Chest emblem
        pygame.draw.rect(inner, color, (4, 6, 2, 2))

    elif cid == "black_mage":
        hat = (40, 40, 70)
        robe = (0, 0, 0)
        face = (255, 220, 180)
        eyes = (255, 255, 255)
        staff = (200, 40, 40)

        # Hat with band
        pygame.draw.polygon(inner, hat, [(2, 3), (7, 3), (5, 0)])
        pygame.draw.rect(inner, hat, (2, 3, 6, 2))
        pygame.draw.rect(inner, color, (2, 4, 6, 1))

        # Face
        pygame.draw.rect(inner, face, (3, 5, 4, 3))
        inner.set_at((4, 6), eyes)
        inner.set_at((5, 6), eyes)

        # Robe with trim
        pygame.draw.rect(inner, robe, (2, 8, 6, 2))
        pygame.draw.rect(inner, color, (2, 8, 6, 2), 1)

        # Staff with gem
        pygame.draw.rect(inner, staff, (0, 1, 1, 8))
        pygame.draw.rect(inner, (255, 200, 0), (0, 0, 1, 1))

    elif cid == "white_mage":
        robe = (240, 240, 240)
        face = (255, 220, 190)
        eyes = (0, 0, 0)
        staff = (40, 160, 60)

        # Robe and hood
        pygame.draw.rect(inner, robe, (2, 0, 6, 10))
        pygame.draw.rect(inner, color, (2, 0, 6, 10), 1)

        # Face
        pygame.draw.rect(inner, face, (3, 2, 4, 3))
        inner.set_at((4, 3), eyes)
        inner.set_at((5, 3), eyes)

        # Trim and staff
        pygame.draw.rect(inner, color, (2, 7, 6, 1))
        pygame.draw.rect(inner, staff, (8, 1, 1, 8))
        pygame.draw.rect(inner, (240, 60, 60), (8, 0, 1, 1))

    else:
        pygame.draw.rect(inner, color, (0, 0, 10, 10))

    s.blit(inner, (1, 1))
    return s

def run(screen, clock, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    # Prebuild icons/text
    icons = [_class_icon(c["id"], c["color"]) for c in CLASSES]
    title = _make_text(TITLE, 20, (255, 230, 140))
    prompt = _make_text("← →  Select   Z/ENTER  Confirm   ESC  Back", 12, (230, 230, 230), shadow=False)

    # Animated background dots
    dots = [{"x": random.randrange(0, vw), "y": random.randrange(0, vh), "s": random.choice([1,1,2])} for _ in range(60)]
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
                    # return a copy so caller can mutate safely
                    chosen = dict(CLASSES[idx])
                    chosen["stats"] = dict(chosen["stats"])
                    return chosen

        # update dots
        for d in dots:
            d["y"] += d["s"] * dt * 20
            if d["y"] > vh:
                d["y"] = -2
                d["x"] = random.randrange(0, vw)

        # draw
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
            pygame.draw.rect(surf, (40, 40, 70), (cx + 4, 28, col_w - 8, vh - 36), 1)

            # icon + name
            ic = icons[i]
            surf.blit(ic, (cx + (col_w - ic.get_width()) // 2, 34))
            nm = _make_text(c["name"], 16, c["color"])
            surf.blit(nm, (cx + (col_w - nm.get_width()) // 2, 50))

            # small separator
            pygame.draw.line(surf, (50, 50, 90), (cx + 10, 66), (cx + col_w - 10, 66))

            # bonuses text
            y = 72
            bonus_color = (230, 230, 230) if i != idx else (255, 255, 180)
            for b in c["bonuses"]:
                line = _make_text(b, 12, bonus_color, shadow=False)
                # wrap if too wide
                if line.get_width() <= col_w - 16:
                    surf.blit(line, (cx + 8, y))
                    y += 12
                else:
                    # crude wrap: split roughly in half
                    mid = len(b) // 2
                    cut = b[:mid].rstrip() + "-"
                    line1 = _make_text(cut, 12, bonus_color, shadow=False)
                    line2 = _make_text(b[mid:].lstrip(), 12, bonus_color, shadow=False)
                    surf.blit(line1, (cx + 8, y))
                    y += 12
                    surf.blit(line2, (cx + 8, y))
                    y += 12

            # selection highlight
            if i == idx:
                pygame.draw.rect(surf, c["color"], (cx + 6, 30, col_w - 12, vh - 40), 1)

        # prompt (blinking)
        if int(t * 2) % 2 == 0:
            surf.blit(prompt, ((vw - prompt.get_width()) // 2, vh - 16))

        # scale out
        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()
