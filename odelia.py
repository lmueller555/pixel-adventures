# odelia.py
"""Opening town: Odelia.

This module implements a simple overworld town with multiple buildings. Each
building has a door that lets the player enter an interior room. The camera
follows the player around the town, scrolling the view when the player moves
close to the edges of the screen.
"""

import pygame
from typing import List

VIRTUAL_SIZE = (256, 144)

# --- player sprite helpers --------------------------------------------------

def _sprite_from_pattern(pattern, palette):
    """Create a pygame Surface from a small ASCII art pattern."""
    height = len(pattern)
    width = len(pattern[0]) if height else 0
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            surf.set_at((x, y), palette[ch])
    return surf


def _player_sprite_for(cid, color):
    """Return a small pixel-art Surface for the given class id."""
    if cid == "knight":
        pattern = [
            "..OOOO..",
            ".OHHHHO.",
            ".OHFFHO.",
            ".OHEEHO.",
            ".OHHHHO.",
            ".OHCCHO.",
            ".OHCCHO.",
            ".OHHHHO.",
            ".OH..HO.",
            ".OH..HO.",
            ".OH..HO.",
            "..O..O..",
        ]
        palette = {
            'O': (30, 30, 70),       # outline
            'H': (170, 170, 190),    # armor
            'F': (255, 220, 180),    # face
            'E': (255, 255, 255),    # eyes
            'C': color,              # class accent
        }
        return _sprite_from_pattern(pattern, palette)

    if cid == "black_mage":
        pattern = [
            "..OOOO..",
            ".OHHHHO.",
            "OHHHHHHO",
            "OHHHHHHO",
            ".OkEEkO.",
            ".OkkkkO.",
            ".OCAACO.",
            ".OCAACO.",
            ".OCAACO.",
            ".OCAACO.",
            ".OCAACO.",
            "..O..O..",
        ]
        palette = {
            'O': (30, 30, 70),       # outline
            'H': (40, 40, 70),       # hat
            'k': (0, 0, 0),          # face shadow
            'E': (255, 255, 255),    # eyes
            'C': (30, 30, 90),       # robe
            'A': color,              # accent trim
        }
        return _sprite_from_pattern(pattern, palette)

    if cid == "white_mage":
        pattern = [
            "..OOOO..",
            ".OHHHHO.",
            "OHFFFFHO",
            "OHFEEFHO",
            ".OHHHHO.",
            ".OWAWWO.",
            ".OWAWWO.",
            ".OAAAAO.",
            ".OWAWWO.",
            ".OWAWWO.",
            ".OWAWWO.",
            "..O..O..",
        ]
        palette = {
            'O': (30, 30, 70),       # outline
            'H': color,              # hood color
            'F': (255, 220, 190),    # face
            'E': (0, 0, 0),          # eyes
            'W': (240, 240, 240),    # robe
            'A': (200, 40, 40),      # red cross accent
        }
        return _sprite_from_pattern(pattern, palette)

    surf = pygame.Surface((8, 8))
    surf.fill(color)
    return surf

# --- Town data --------------------------------------------------------------

WORLD_W, WORLD_H = 480, 360


def _make_interior(size, floor_color):
    """Return interior data for a building.

    The interior consists of a pre-rendered surface with simple walls and a
    doorway, as well as the rectangle representing that doorway for
    interaction logic.
    """
    surf = pygame.Surface(size)
    surf.fill(floor_color)

    wall_color = (120, 80, 40)
    t = 8  # wall thickness
    # Walls
    pygame.draw.rect(surf, wall_color, (0, 0, size[0], t))  # top
    pygame.draw.rect(surf, wall_color, (0, 0, t, size[1]))  # left
    pygame.draw.rect(surf, wall_color, (size[0] - t, 0, t, size[1]))  # right
    pygame.draw.rect(surf, wall_color, (0, size[1] - t, size[0], t))  # bottom

    # Doorway centered along the bottom wall
    door = pygame.Rect(size[0] // 2 - 8, size[1] - t, 16, t)
    pygame.draw.rect(surf, (100, 70, 40), door)

    return {"size": size, "door": door, "surface": surf}


def _make_buildings() -> List[dict]:
    buildings = []
    rows, cols = 3, 4
    w, h = 60, 60
    floor_colors = [
        (190, 170, 120),
        (170, 170, 190),
        (150, 180, 150),
        (190, 170, 170),
    ]
    for r in range(rows):
        for c in range(cols):
            bx = 40 + c * 100
            by = 40 + r * 100
            rect = pygame.Rect(bx, by, w, h)
            solid = pygame.Rect(bx, by, w, h - 8)
            door = pygame.Rect(bx + w // 2 - 8, by + h - 8, 16, 8)

            interior = _make_interior((160, 120), floor_colors[(r * cols + c) % len(floor_colors)])

            buildings.append({
                "rect": rect,
                "solid": solid,
                "door": door,
                "interior": interior,
            })
    return buildings

# --- Main loop --------------------------------------------------------------

def run(screen, clock, chosen_class, virtual_size=VIRTUAL_SIZE):
    """Run the Odelia town scene."""
    vw, vh = virtual_size
    game_surf = pygame.Surface(virtual_size)

    # Player setup
    sprite = _player_sprite_for(chosen_class["id"], chosen_class["color"])
    stats = chosen_class["stats"]
    speed = 60 * stats.get("spd_mult", 1.0)
    player = pygame.Rect(WORLD_W // 2 - 4, WORLD_H // 2 - 4, 8, 8)

    buildings = _make_buildings()

    mode = "town"  # or "interior"
    current = None
    door_cooldown = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "title"

        door_cooldown = max(0.0, door_cooldown - dt)

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        )
        if move.length_squared() > 0:
            move = move.normalize()
        vel = move * speed * dt

        if mode == "town":
            # movement and collision
            player.x += int(round(vel.x))
            for b in buildings:
                if player.colliderect(b["solid"]):
                    if vel.x > 0: player.right = b["solid"].left
                    elif vel.x < 0: player.left = b["solid"].right
            player.y += int(round(vel.y))
            for b in buildings:
                if player.colliderect(b["solid"]):
                    if vel.y > 0: player.bottom = b["solid"].top
                    elif vel.y < 0: player.top = b["solid"].bottom
            player.clamp_ip(pygame.Rect(0, 0, WORLD_W, WORLD_H))

            # door entry
            if door_cooldown <= 0:
                for b in buildings:
                    if player.colliderect(b["door"]):
                        mode = "interior"
                        current = b
                        d = b["interior"]["door"]
                        player = pygame.Rect(0, 0, 8, 8)
                        player.midbottom = (d.centerx, d.top)
                        door_cooldown = 0.5
                        break

            # camera
            cam_x = player.centerx - vw // 2
            cam_y = player.centery - vh // 2
            cam_x = max(0, min(cam_x, WORLD_W - vw))
            cam_y = max(0, min(cam_y, WORLD_H - vh))

            # draw town
            game_surf.fill((80, 170, 80))
            for b in buildings:
                r = b["rect"]
                pygame.draw.rect(game_surf, (160, 110, 60), (r.x - cam_x, r.y - cam_y, r.w, r.h))
                d = b["door"]
                pygame.draw.rect(game_surf, (100, 70, 40), (d.x - cam_x, d.y - cam_y, d.w, d.h))
            sprite_rect = sprite.get_rect(center=(player.centerx - cam_x, player.centery - cam_y))
            game_surf.blit(sprite, sprite_rect)

        else:  # interior
            size = current["interior"]["size"]
            interior_rect = pygame.Rect(0, 0, *size)

            player.x += int(round(vel.x))
            player.y += int(round(vel.y))
            player.clamp_ip(interior_rect)

            d = current["interior"]["door"]
            if door_cooldown <= 0 and player.colliderect(d):
                # exit to town
                mode = "town"
                player = pygame.Rect(0, 0, 8, 8)
                player.midtop = (current["door"].centerx, current["door"].bottom)
                current = None
                door_cooldown = 0.5
                continue

            surf = current["interior"]["surface"]
            game_surf.blit(surf, (0, 0))
            sprite_rect = sprite.get_rect(center=player.center)
            game_surf.blit(sprite, sprite_rect)

        pygame.transform.scale(game_surf, screen.get_size(), screen)
        pygame.display.flip()

# End of odelia.py
