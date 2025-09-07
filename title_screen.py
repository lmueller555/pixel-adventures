# title_screen.py
# Pixel Adventures — Title Screen
# Drawn at low "virtual" resolution and scaled to fill the screen.

import math
import random
import pygame

VIRTUAL_SIZE = (256, 144)   # internal pixel canvas (virtual)
TITLE        = "Pixel Adventures"

# --- tiny helpers ------------------------------------------------------------
def _make_text(text, size, color, shadow=True):
    font = pygame.font.Font(None, size)  # default font; antialias off for pixel look
    surf = font.render(text, False, color)
    if shadow:
        sh = font.render(text, False, (0, 0, 0))
        out = pygame.Surface((surf.get_width()+1, surf.get_height()+1), pygame.SRCALPHA)
        out.blit(sh, (1, 1))
        out.blit(surf, (0, 0))
        return out
    return surf

class Starfield:
    def __init__(self, w, h, count=60):
        self.w, self.h = w, h
        # parallax: slow, medium, fast layers
        self.layers = []
        for speed, density, color in [(12, 0.35, (120,120,120)), (24, 0.45, (190,190,190)), (40, 0.20, (255,255,255))]:
            n = max(1, int(count * density))
            stars = [{
                "x": random.randrange(0, w),
                "y": random.randrange(0, h),
                "spd": speed,
                "col": color
            } for _ in range(n)]
            self.layers.append(stars)

    def update(self, dt):
        for stars in self.layers:
            for s in stars:
                s["y"] += s["spd"] * dt
                if s["y"] >= self.h:
                    s["y"] = -1
                    s["x"] = random.randrange(0, self.w)

    def draw(self, surf):
        for stars in self.layers:
            for s in stars:
                surf.set_at((int(s["x"]), int(s["y"])), s["col"])

def run(screen, clock, virtual_size=VIRTUAL_SIZE):
    vw, vh = virtual_size
    game_surf = pygame.Surface(virtual_size)  # low-res canvas
    starfield = Starfield(vw, vh)
    t = 0.0

    title = _make_text(TITLE, 24, (255, 230, 120))
    subtitle = _make_text("Press [Z] or [ENTER] to start", 12, (240, 240, 240))
    exit_hint = _make_text("Press [ESC] to quit", 12, (200, 200, 200), shadow=False)

    # simple bobbing "hero" placeholder (8x8)
    hero_frames = []
    for c in [(90,200,255), (70,170,235)]:
        f = pygame.Surface((8, 8), pygame.SRCALPHA)
        f.fill((0,0,0,0))
        pygame.draw.rect(f, (30, 30, 70), (0, 0, 8, 8))  # border
        pygame.draw.rect(f, c, (1, 1, 6, 6))             # body
        pygame.draw.rect(f, (255,255,255), (3, 2, 2, 2)) # "eyes"
        hero_frames.append(f)

    frame_idx = 0
    frame_accum = 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt
        frame_accum += dt
        if frame_accum >= 0.25:
            frame_accum = 0.0
            frame_idx = (frame_idx + 1) % len(hero_frames)

        # --- input ------------------------------------------------------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE,):
                    return "quit"
                if e.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    return "start"

        # --- update -----------------------------------------------------------
        starfield.update(dt)

        # --- draw virtual frame ----------------------------------------------
        game_surf.fill((10, 10, 20))
        starfield.draw(game_surf)

        # subtle horizon gradient
        for y in range(vh):
            shade = 10 + int(30 * (y / vh))
            pygame.draw.line(game_surf, (shade, shade, 40), (0, y), (vw, y))

        # title bob
        bob = int(math.sin(t * 2.0) * 2)
        tx = (vw - title.get_width()) // 2
        ty = 22 + bob
        game_surf.blit(title, (tx, ty))

        # hero bob
        hero = hero_frames[frame_idx]
        hx = vw // 2 - hero.get_width() // 2
        hy = ty + title.get_height() + 8 + int(math.sin(t * 3.0) * 2)
        game_surf.blit(hero, (hx, hy))

        # blinking prompt
        if int(t * 2) % 2 == 0:
            px = (vw - subtitle.get_width()) // 2
            py = vh - 34
            game_surf.blit(subtitle, (px, py))

        # exit hint
        ex = (vw - exit_hint.get_width()) // 2
        game_surf.blit(exit_hint, (ex, vh - 18))

        # --- scale to window --------------------------------------------------
        pygame.transform.scale(game_surf, screen.get_size(), screen)
        pygame.display.flip()
