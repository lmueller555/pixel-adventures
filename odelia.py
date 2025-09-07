# odelia.py
"""Opening town: Odelia.

This module implements a simple overworld town with multiple buildings. Each
building has a door that lets the player enter an interior room. The camera
follows the player around the town, scrolling the view when the player moves
close to the edges of the screen.
"""

import pygame
from typing import List
import buildings as bld

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
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        outline = (30, 30, 70)
        armor = (170, 170, 190)
        face = (255, 220, 180)
        eyes = (255, 255, 255)
        blade = (210, 210, 220)
        hilt = (120, 80, 40)
        shield = (160, 130, 70)

        # Helmet and body
        pygame.draw.rect(surf, armor, (4, 1, 8, 4))
        pygame.draw.rect(surf, armor, (4, 6, 8, 8))
        pygame.draw.rect(surf, outline, (4, 1, 8, 4), 1)
        pygame.draw.rect(surf, outline, (4, 6, 8, 8), 1)

        # Plume and chest emblem
        pygame.draw.rect(surf, color, (8, 0, 2, 1))
        pygame.draw.rect(surf, color, (7, 8, 2, 2))

        # Face
        pygame.draw.rect(surf, face, (6, 2, 4, 3))
        surf.set_at((7, 3), eyes)
        surf.set_at((8, 3), eyes)

        # Shield
        pygame.draw.rect(surf, outline, (0, 7, 4, 6))
        pygame.draw.rect(surf, shield, (1, 8, 2, 4))
        pygame.draw.rect(surf, color, (1, 9, 2, 2))

        # Sword
        pygame.draw.rect(surf, blade, (14, 3, 1, 10))
        pygame.draw.rect(surf, hilt, (13, 9, 3, 2))

        return surf

    if cid == "black_mage":
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        hat = (40, 40, 70)
        robe = (0, 0, 0)
        face = (255, 220, 180)
        eyes = (255, 255, 255)
        staff = (200, 40, 40)

        # Hat with band
        pygame.draw.polygon(surf, hat, [(4, 6), (11, 6), (7, 0)])
        pygame.draw.rect(surf, hat, (4, 6, 8, 2))
        pygame.draw.rect(surf, color, (4, 7, 8, 1))

        # Face
        pygame.draw.rect(surf, face, (6, 8, 4, 4))
        surf.set_at((7, 9), eyes)
        surf.set_at((8, 9), eyes)

        # Robe with belt and trim
        pygame.draw.rect(surf, robe, (4, 12, 8, 4))
        pygame.draw.rect(surf, color, (4, 12, 8, 4), 1)
        pygame.draw.rect(surf, color, (4, 13, 8, 1))
        pygame.draw.rect(surf, color, (4, 15, 8, 1))

        # Staff with gem
        pygame.draw.rect(surf, staff, (1, 3, 2, 13))
        pygame.draw.rect(surf, (255, 200, 0), (1, 3, 2, 2))

        return surf

    if cid == "white_mage":
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        robe = (240, 240, 240)
        face = (255, 220, 190)
        eyes = (0, 0, 0)
        staff = (40, 160, 60)

        # Hood and robe with trim
        pygame.draw.rect(surf, robe, (4, 1, 8, 14))
        pygame.draw.rect(surf, color, (4, 1, 8, 14), 1)
        pygame.draw.rect(surf, color, (4, 14, 8, 1))

        # Face
        pygame.draw.rect(surf, face, (6, 4, 4, 3))
        surf.set_at((7, 5), eyes)
        surf.set_at((8, 5), eyes)

        # Chest mark
        pygame.draw.rect(surf, color, (7, 9, 2, 1))
        pygame.draw.rect(surf, color, (8, 8, 1, 3))

        # Staff with gem
        pygame.draw.rect(surf, staff, (13, 2, 2, 13))
        pygame.draw.rect(surf, (240, 60, 60), (13, 2, 2, 2))

        return surf

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
    result = []
    rows, cols = 3, 4
    floor_colors = [
        (190, 170, 120),
        (170, 170, 190),
        (150, 180, 150),
        (190, 170, 170),
    ]
    types = [bld.House, bld.Inn, bld.ItemShop]
    idx = 0
    for r in range(rows):
        for c in range(cols):
            bx = 40 + c * 100
            by = 40 + r * 100
            cls = types[idx % len(types)]
            bobj = cls()
            w, h = bobj.size
            rect = pygame.Rect(bx, by, w, h)
            solid = bobj.solid.move(bx, by)
            door = bobj.door.move(bx, by)
            interior = _make_interior((160, 120), floor_colors[idx % len(floor_colors)])
            result.append({
                "rect": rect,
                "solid": solid,
                "door": door,
                "interior": interior,
                "surface": bobj.surface,
            })
            idx += 1
    return result

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
                game_surf.blit(b["surface"], (r.x - cam_x, r.y - cam_y))
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
