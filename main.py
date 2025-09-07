# main.py
# Pixel Adventures — Flow: Title -> Class Select -> Game -> Title

import sys
import pygame
import title_screen
import class_select
import opening_sequence

VIRTUAL_SIZE = title_screen.VIRTUAL_SIZE
CAPTION      = "Pixel Adventures"

def _sprite_from_pattern(pattern, palette):
    """Create a pygame Surface from a small ASCII art pattern.

    `pattern` is a list of equal-length strings where each character maps to a
    color in `palette`. The character `.` represents transparency.
    """
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

    # fallback simple block if class unknown
    surf = pygame.Surface((8, 8))
    surf.fill(color)
    return surf

def run_game(screen, clock, chosen_class):
    vw, vh = VIRTUAL_SIZE
    game_surf = pygame.Surface(VIRTUAL_SIZE)

    # Use class stats
    stats = chosen_class["stats"]
    color = chosen_class["color"]
    name  = chosen_class["name"]

    # Build player sprite for this class
    sprite = _player_sprite_for(chosen_class["id"], color)

    base_speed = 60
    speed      = base_speed * stats.get("spd_mult", 1.0)
    magnet     = stats.get("magnet", 12)
    special    = 0.0
    special_rate = stats.get("special_rate", 1.0)

    # player rect & simple walls
    player = pygame.Rect(vw//2 - 4, vh//2 - 4, 8, 8)
    walls = [pygame.Rect(20, 40, 216, 6), pygame.Rect(40, 88, 176, 6)]

    # coins
    coins = [pygame.Rect(16 + i*24, 24 + (i%3)*18, 4, 4) for i in range(7)]
    score = 0

    # HUD font
    font = pygame.font.Font(None, 14)
    big  = pygame.font.Font(None, 18)

    # small helper
    def attract_coin(c):
        # pull coins toward player if within "magnet" radius
        pc = pygame.Vector2(player.center)
        cc = pygame.Vector2(c.center)
        v = pc - cc
        dist = v.length()
        if dist < magnet and dist > 0:
            step = max(1.0, dist * 0.12)  # proportional pull
            move = v.normalize() * step
            c.x += int(round(move.x))
            c.y += int(round(move.y))

    # For Black Mage: extra special on coin pickup (simple perk)
    def on_coin_pickup():
        nonlocal special
        if chosen_class["id"] == "black_mage":
            special = min(100.0, special + 8)

    while True:
        dt = clock.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "title"

        # input
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN]  or keys[pygame.K_s]) - (keys[pygame.K_UP]   or keys[pygame.K_w])
        )
        if move.length_squared() > 0:
            move = move.normalize()
        vel = move * speed * dt

        # movement + wall collision
        player.x += int(round(vel.x))
        for w in walls:
            if player.colliderect(w):
                if vel.x > 0: player.right = w.left
                elif vel.x < 0: player.left = w.right
        player.y += int(round(vel.y))
        for w in walls:
            if player.colliderect(w):
                if vel.y > 0: player.bottom = w.top
                elif vel.y < 0: player.top = w.bottom
        player.clamp_ip(pygame.Rect(0, 0, vw, vh))

        # coins
        for c in coins[:]:
            attract_coin(c)
            if player.colliderect(c):
                coins.remove(c)
                score += 1
                on_coin_pickup()

        # Special meter passive fill (differs by class)
        special = min(100.0, special + 12.0 * special_rate * dt)

        # draw
        game_surf.fill((12, 12, 18))
        for y in range(0, vh, 8):
            pygame.draw.line(game_surf, (18, 18, 26), (0, y), (vw, y))
        for x in range(0, vw, 8):
            pygame.draw.line(game_surf, (18, 18, 26), (x, 0), (x, vh))

        for w in walls:
            pygame.draw.rect(game_surf, (60, 60, 110), w)
            pygame.draw.rect(game_surf, (20, 20, 50), w.inflate(2, 2), 1)

        for c in coins:
            pygame.draw.rect(game_surf, (255, 208, 52), c)
            game_surf.set_at((c.centerx, c.top-1), (255, 255, 140))

        # player sprite
        sprite_rect = sprite.get_rect(center=player.center)
        game_surf.blit(sprite, sprite_rect)

        # HUD
        hud_l = big.render(name, False, (230, 230, 230))
        game_surf.blit(hud_l, (4, 4))
        hud_r = font.render(f"Score: {score}", False, (200, 200, 200))
        game_surf.blit(hud_r, (vw - hud_r.get_width() - 4, 6))

        # Special bar
        pygame.draw.rect(game_surf, (40, 40, 70), (4, vh - 10, vw - 8, 6), 1)
        fill_w = int((vw - 10) * (special / 100.0))
        pygame.draw.rect(game_surf, (120, 220, 255), (5, vh - 9, fill_w, 4))

        # scale
        pygame.transform.scale(game_surf, screen.get_size(), screen)
        pygame.display.flip()

def main():
    pygame.init()
    pygame.display.set_caption(CAPTION)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    while True:
        # Title
        r = title_screen.run(screen, clock, VIRTUAL_SIZE)
        if r == "quit": break

        # Class Select
        choice = class_select.run(screen, clock, VIRTUAL_SIZE)
        if choice in ("quit", "back"):  # back returns to title, quit exits
            if choice == "quit": break
            else: continue

        # Opening battle sequence
        opening_sequence.run(screen, clock, VIRTUAL_SIZE)

        # Game
        r = run_game(screen, clock, choice)
        if r == "quit": break
        # if "title", loop restarts at title

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
