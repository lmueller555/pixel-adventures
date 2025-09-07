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
import class_select

VIRTUAL_SIZE = (1024, 576)

# --- player sprite helper ---------------------------------------------------

def _player_sprite_for(cid, color):
    """Return walk animation frames for the chosen class."""
    return [class_select._class_icon(cid, color, with_panel=False, frame=f) for f in (0, 1)]

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
    sprite_frames = _player_sprite_for(chosen_class["id"], chosen_class["color"])
    anim_t = 0.0
    sprite_frame = 0
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
            if move.length_squared() > 0:
                anim_t += dt * 8
                sprite_frame = int(anim_t) % len(sprite_frames)
            else:
                anim_t = 0.0
                sprite_frame = 0
            current = sprite_frames[sprite_frame]
            sprite_rect = current.get_rect(midbottom=(player.centerx - cam_x, player.bottom - cam_y))
            game_surf.blit(current, sprite_rect)

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
            if move.length_squared() > 0:
                anim_t += dt * 8
                sprite_frame = int(anim_t) % len(sprite_frames)
            else:
                anim_t = 0.0
                sprite_frame = 0
            current = sprite_frames[sprite_frame]
            sprite_rect = current.get_rect(midbottom=player.midbottom)
            game_surf.blit(current, sprite_rect)

        pygame.transform.scale(game_surf, screen.get_size(), screen)
        pygame.display.flip()

# End of odelia.py
