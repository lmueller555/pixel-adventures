# class_select.py
# Pixel Adventures — Class Selection Screen (after Title)
# Uses same low-res virtual canvas & integer scale for crisp pixels.

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

def _class_icon(color):
    # simple 12x12 icon with border & “eyes”
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.rect(s, (25, 25, 45), (0, 0, 12, 12))   # border
    pygame.draw.rect(s, color, (1, 1, 10, 10))          # body
    s.set_at((4, 4), (255, 255, 255))
    s.set_at((7, 4), (255, 255, 255))
    return s

def run(screen, clock, scale, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    # Prebuild icons/text
    icons = [_class_icon(c["color"]) for c in CLASSES]
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
        pygame.transform.scale(surf, (vw * scale, vh * scale), screen)
        pygame.display.flip()
