import math
import random
import pygame
import buildings as bld

# ─────────────────────────────────────────────────────────────────────────────
# Pixel Adventures — Opening Cinematic
# Shots:
#   0) Establishing: morning in Odelia, wide pan (life is normal)
#   1) Medium follow: hero strolls by shops (closer, slower dolly)
#   2) Sky tilt: meteor streak enters (rack zoom + tilt)
#   3) Impact & destruction montage: shake, flames, debris
#   4) Hard flash → Bedroom: wake from dream
#   5) Walk outside: the town is safe (relief wide)
#   (Any key press skips to end)
# ─────────────────────────────────────────────────────────────────────────────

# Durations (seconds)
SHOT_DUR = [4.0, 4.0, 3.0, 3.5, 3.5, 4.0]
FPS = 60

# Cinematic black bars (letterbox)
LETTERBOX = 8  # virtual pixels (top/bot)

# Colors
SKY_MORN_TOP = (30, 50, 95)
SKY_MORN_BOT = (120, 160, 210)
SKY_EVE_TOP  = (25, 20, 40)
SKY_EVE_BOT  = (80, 50, 80)
GROUND_LINE  = (60, 60, 90)

WHITE = (255, 255, 255)
SMOKE_COL = (90, 90, 110)
EMBER_COL = (255, 150, 60)
FIRE_OUTER = (255, 120, 0)
FIRE_INNER = (255, 220, 160)
DUST_COL = (150, 130, 100)

TITLE_COL = (245, 230, 160)

# World size (bigger than virtual so we can pan/zoom without blur)
WORLD_W_MULT = 3
WORLD_H_MULT = 2


# ────────────────────────────── Utilities ────────────────────────────────────

def _charred_surface(src: pygame.Surface) -> pygame.Surface:
    """Darken and mute a building surface."""
    s = src.copy()
    overlay = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    overlay.fill((35, 35, 35, 220))
    s.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return s

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))

def ease_in_out(t):
    # smoothstep-ish easing for camera moves
    return t * t * (3 - 2 * t)

def draw_vgradient(surf, top_col, bot_col):
    w, h = surf.get_size()
    for y in range(h):
        t = y / max(1, h - 1)
        c = (int(lerp(top_col[0], bot_col[0], t)),
             int(lerp(top_col[1], bot_col[1], t)),
             int(lerp(top_col[2], bot_col[2], t)))
        pygame.draw.line(surf, c, (0, y), (w, y))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ────────────────────────────── Camera ───────────────────────────────────────

class Camera:
    def __init__(self, vw, vh, world_w, world_h):
        self.vw, self.vh = vw, vh
        self.world = pygame.Rect(0, 0, world_w, world_h)
        self.cx, self.cy = world_w // 2, world_h // 2
        self.zoom = 1.0
        self.shake_mag = 0.0
        self.shake_decay = 0.9

    def set(self, cx=None, cy=None, zoom=None):
        if cx is not None: self.cx = cx
        if cy is not None: self.cy = cy
        if zoom is not None: self.zoom = max(0.5, min(2.0, zoom))

    def add_shake(self, amount):
        self.shake_mag = max(self.shake_mag, amount)

    def present(self, world_surface, dest_surface):
        """Crop & scale world to virtual size with integer-ish zoom and shake."""
        # Shake
        ox = random.randint(-int(self.shake_mag), int(self.shake_mag)) if self.shake_mag > 0 else 0
        oy = random.randint(-int(self.shake_mag), int(self.shake_mag)) if self.shake_mag > 0 else 0
        self.shake_mag *= self.shake_decay

        # Compute source rect based on zoom
        src_w = int(self.vw / self.zoom)
        src_h = int(self.vh / self.zoom)
        cx = int(self.cx + ox)
        cy = int(self.cy + oy)
        left = clamp(cx - src_w // 2, 0, self.world.w - src_w)
        top  = clamp(cy - src_h // 2, 0, self.world.h - src_h)
        src_rect = pygame.Rect(left, top, src_w, src_h)

        # Crop and scale to dest
        region = world_surface.subsurface(src_rect)
        frame = pygame.transform.scale(region, (self.vw, self.vh))
        dest_surface.blit(frame, (0, 0))


# ────────────────────────────── Particles ────────────────────────────────────

class Particle:
    __slots__ = ("x","y","vx","vy","life","col","size","grav","fade")

    def __init__(self, x,y, vx,vy, life, col, size=2, grav=0.0, fade=True):
        self.x,self.y = x,y
        self.vx,self.vy = vx,vy
        self.life = life
        self.col = col
        self.size = size
        self.grav = grav
        self.fade = fade

    def update(self, dt):
        self.vy += self.grav * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        if self.life <= 0: return
        c = self.col
        if self.fade:
            a = clamp(int(255 * (self.life)), 0, 255)
            c = (c[0], c[1], c[2], a)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill(c)
        surf.blit(s, (int(self.x), int(self.y)))


# ────────────────────────────── Scene Builders ───────────────────────────────

def build_town(world, base_y):
    """Place three buildings across the plaza."""
    house = bld.House().surface
    inn   = bld.Inn().surface
    shop  = bld.ItemShop().surface

    # positions in world coords
    cx = world.get_width() // 2
    x0 = cx - 160
    x1 = cx
    x2 = cx + 160
    rects = [
        house.get_rect(midbottom=(x0, base_y)),
        inn.get_rect(midbottom=(x1, base_y)),
        shop.get_rect(midbottom=(x2, base_y)),
    ]
    return [house, inn, shop], rects

def draw_ground(world, base_y):
    pygame.draw.line(world, GROUND_LINE, (0, base_y), (world.get_width(), base_y))

def draw_people(world, rects, t, lead_pos=None):
    """Tiny NPCs dots/rects to show life."""
    # Vendor
    shop_r = rects[2]
    pygame.draw.rect(world, (210, 180, 120), (shop_r.centerx - 3, shop_r.top - 8, 6, 6))
    # Shopper walking
    sx = rects[2].x - 40 + int(math.sin(t * 0.7) * 12)
    pygame.draw.rect(world, (150, 200, 255), (sx, rects[2].bottom - 6, 4, 4))
    # Child playing
    hx = rects[0].right + 20 + int(math.sin(t * 1.2) * 6)
    pygame.draw.rect(world, (255, 200, 200), (hx, rects[0].bottom - 6, 3, 3))
    # Lead character (optional)
    if lead_pos:
        x, y = lead_pos
        pygame.draw.rect(world, (90, 200, 255), (x - 4, y - 10, 8, 10))
        world.set_at((x, y - 8), WHITE)

def draw_buildings(world, b_surfs, b_rects, destroyed=False, flames=None):
    if destroyed:
        charred = getattr(draw_buildings, "_charred", None)
        if charred is None:
            charred = [_charred_surface(s) for s in b_surfs]
            draw_buildings._charred = charred
        for s, r in zip(charred, b_rects):
            world.blit(s, r)
        # flames rendered separately
    else:
        for s, r in zip(b_surfs, b_rects):
            world.blit(s, r)

def draw_bedroom(world, base_y):
    """Simple cozy room: bed, window, desk."""
    w, h = world.get_size()
    # background walls
    room = pygame.Rect(w//2 - 120, base_y - 100, 240, 95)
    pygame.draw.rect(world, (30, 30, 50), room)
    pygame.draw.rect(world, (50, 50, 90), room, 1)
    # window with morning gradient
    win = pygame.Rect(room.x + 12, room.y + 10, 60, 40)
    pygame.draw.rect(world, (20, 20, 30), win)
    for y in range(win.height):
        t = y / max(1, win.height - 1)
        c = (int(lerp(80, 160, t)), int(lerp(120, 200, t)), int(lerp(180, 255, t)))
        pygame.draw.line(world, c, (win.x + 1, win.y + y), (win.right - 2, win.y + y))
    pygame.draw.rect(world, (80, 80, 120), win, 1)

    # bed
    bed = pygame.Rect(room.centerx - 60, room.bottom - 28, 120, 18)
    pygame.draw.rect(world, (120, 90, 70), bed)          # frame
    pygame.draw.rect(world, (200, 200, 220), bed.inflate(-8, -8))  # sheets
    pillow = pygame.Rect(bed.x + 10, bed.y + 4, 24, 10)
    pygame.draw.rect(world, (230, 230, 240), pillow)

    # desk & book
    desk = pygame.Rect(room.x + 140, bed.y - 24, 60, 14)
    pygame.draw.rect(world, (110, 80, 60), desk)
    pygame.draw.rect(world, (200, 180, 130), (desk.x + 6, desk.y + 4, 22, 6))  # book

    return room, bed, pillow

def draw_letterbox(surf, h=LETTERBOX):
    w, vh = surf.get_size()
    if h > 0:
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, w, h))
        pygame.draw.rect(surf, (0, 0, 0), (0, vh - h, w, h))

def draw_fade(surf, alpha):
    if alpha <= 0: return
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(alpha)))
    surf.blit(overlay, (0, 0))

def draw_flash(surf, alpha):
    if alpha <= 0: return
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, int(alpha)))
    surf.blit(overlay, (0, 0))

def title_card(surf, text, color=TITLE_COL):
    font = pygame.font.Font(None, 24)
    tx = font.render(text, False, color)
    surf.blit(tx, ((surf.get_width() - tx.get_width()) // 2, 12))


# ────────────────────────────── Main Cinematic ───────────────────────────────

def run(screen, clock, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    # Build world canvas bigger than the virtual viewport
    world_w = vw * WORLD_W_MULT
    world_h = vh * WORLD_H_MULT
    world = pygame.Surface((world_w, world_h), pygame.SRCALPHA)

    base_y = world_h - 64  # ground line
    b_surfs, b_rects = build_town(world, base_y)

    # Hero starting position (world coords)
    hero_x = b_rects[0].centerx
    hero_y = base_y
    hero_walk_dir = 1

    # Meteor
    meteor = pygame.Rect(world_w // 2 - 8, -40, 16, 16)
    meteor_v = pygame.Vector2(0, 260)
    meteor_active = False
    impact_point = (b_rects[1].centerx, b_rects[1].top)

    # Particles
    particles = []  # Particle instances
    flames = []     # flame rectangles with timers
    explosions = 0

    # Camera
    cam = Camera(vw, vh, world_w, world_h)

    # Timing
    shot_idx = 0
    shot_t = 0.0
    total_frames = 0

    # Fade & flash
    fade_in = 255
    fade_out = 0
    flash = 0

    # Dream flag
    dream = True
    destroyed = False

    # Pre-compute cumulative durations to allow key-skip logic
    total_dur = sum(SHOT_DUR)
    max_frames = int(total_dur * FPS)

    # Cinematic title (beginning only)
    title_shown = True

    while total_frames < max_frames:
        dt = clock.tick(FPS) / 1000.0
        shot_t += dt
        total_frames += 1

        # Input: skip cinematic
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_z
            ):
                return

        # Shot progression
        if shot_t >= SHOT_DUR[shot_idx]:
            shot_t = 0.0
            shot_idx += 1
            # transitions
            if shot_idx == 2:
                # prepare meteor sequence
                meteor_active = True
            if shot_idx == 3:
                # harder letterbox & shake
                cam.add_shake(4)
            if shot_idx == 4:
                # hard white flash into bedroom
                flash = 255
                destroyed = False
                dream = False
                meteor_active = False
            if shot_idx >= len(SHOT_DUR):
                break

        # Draw world fresh each frame
        world.fill((0, 0, 0, 0))

        # Sky
        if dream:
            draw_vgradient(world, SKY_MORN_TOP, SKY_MORN_BOT)
        else:
            draw_vgradient(world, SKY_MORN_TOP, SKY_MORN_BOT)

        # Ground line
        draw_ground(world, base_y)

        # ── Shot logic ────────────────────────────────────────────────────────
        if shot_idx == 0:
            # (0) Establishing wide pan across the plaza
            # Camera slowly pans from left to center, slight zoom in.
            p = ease_in_out(shot_t / SHOT_DUR[0])
            cam.set(
                cx=int(lerp(vw // 2, world_w // 2, p)),
                cy=int(base_y - vh // 3),
                zoom=lerp(0.9, 1.05, p),
            )

            draw_buildings(world, b_surfs, b_rects, destroyed=False)

            # Hero exits house; walk a bit toward inn
            hero_x = lerp(b_rects[0].centerx, b_rects[1].centerx - 40, p)
            draw_people(world, b_rects, total_frames / FPS, lead_pos=(int(hero_x), int(hero_y)))
            title_card(world, "Odelia")

        elif shot_idx == 1:
            # (1) Medium follow: hero strolls by shops, vendor & child visible
            p = ease_in_out(shot_t / SHOT_DUR[1])
            cam.set(
                cx=int(lerp(b_rects[0].centerx + 40, b_rects[2].centerx - 40, p)),
                cy=int(base_y - 40),
                zoom=lerp(1.05, 1.15, p),
            )
            draw_buildings(world, b_surfs, b_rects, destroyed=False)
            hero_x += 24 * dt * hero_walk_dir
            if hero_x > b_rects[2].centerx - 10:
                hero_walk_dir = -1
            if hero_x < b_rects[0].centerx + 10:
                hero_walk_dir = 1
            draw_people(world, b_rects, total_frames / FPS, lead_pos=(int(hero_x), int(hero_y)))
            title_shown = False

        elif shot_idx == 2:
            # (2) Sky tilt & meteor arrival: tilt up by sliding camera higher and zooming in
            p = ease_in_out(shot_t / SHOT_DUR[2])
            cam.set(
                cx=int(lerp(b_rects[1].centerx, b_rects[1].centerx, 1)),
                cy=int(lerp(base_y - 40, base_y - 130, p)),  # tilt up
                zoom=lerp(1.0, 1.25, p),
            )
            draw_buildings(world, b_surfs, b_rects, destroyed=False)
            draw_people(world, b_rects, total_frames / FPS, lead_pos=(int(hero_x), int(hero_y)))

            if meteor_active:
                # meteor streak: add ember particles
                meteor.x = int(lerp(world_w//2 - 140, impact_point[0] - 8, p))
                meteor.y = int(lerp(-60, impact_point[1] - 60, p))
                pygame.draw.ellipse(world, (240, 240, 90), meteor)
                # trail
                for _ in range(2):
                    particles.append(Particle(
                        meteor.centerx + random.randint(-2, 2),
                        meteor.centery + random.randint(-2, 2),
                        -60 + random.randint(-20, 0),
                        -20 + random.randint(-10, 10),
                        life=0.6, col=EMBER_COL, size=2, grav=0.0, fade=True
                    ))

        elif shot_idx == 3:
            # (3) Impact & destruction: shake, flames, debris, zoom punches
            p = shot_t / SHOT_DUR[3]
            cam.set(
                cx=b_rects[1].centerx + random.randint(-4, 4),
                cy=int(lerp(base_y - 110, base_y - 60, ease_in_out(p))),
                zoom=lerp(1.25, 1.05, p),
            )
            # Buildings switch to charred after impact begins
            draw_buildings(world, b_surfs, b_rects, destroyed=True)

            # First frames: big shock flash & explosion ring
            if shot_t < 0.6:
                # impact point
                cx, cy = impact_point
                r = int(lerp(6, 60, shot_t / 0.6))
                pygame.draw.circle(world, (255, 180, 90), (cx, cy), r, 2)
                cam.add_shake(2.5)
                if explosions == 0:
                    explosions = 1
                    # spawn debris burst
                    for _ in range(50):
                        ang = random.random() * math.tau
                        spd = random.uniform(80, 220)
                        particles.append(Particle(
                            cx, cy,
                            math.cos(ang)*spd, math.sin(ang)*spd,
                            life=random.uniform(0.5, 1.2),
                            col=DUST_COL, size=2, grav=120.0, fade=True
                        ))

            # Flames randomly over charred buildings
            if random.random() < 0.25:
                b = random.choice(b_rects)
                r = pygame.Rect(
                    random.randint(b.left, b.right - 6),
                    random.randint(b.top + 4, b.bottom - 10),
                    6, 10
                )
                flames.append([r, random.uniform(0.8, 1.6)])

            # Render flames
            for fl in flames[:]:
                rect, life = fl
                # flicker
                rect.y += random.randint(-1, 1)
                # draw
                pygame.draw.rect(world, FIRE_OUTER, rect)
                inner = rect.inflate(-2, -2)
                pygame.draw.rect(world, FIRE_INNER, inner)
                # smoke particles
                if random.random() < 0.3:
                    particles.append(Particle(
                        rect.centerx, rect.top,
                        random.uniform(-10, 10), random.uniform(-30, -10),
                        life=random.uniform(0.8, 1.5),
                        col=SMOKE_COL, size=2, grav=-5.0, fade=True
                    ))
                # decay
                fl[1] -= dt
                if fl[1] <= 0: flames.remove(fl)

            # Add persistent smoke plume
            if random.random() < 0.7:
                cx, cy = impact_point
                particles.append(Particle(
                    cx + random.randint(-12, 12), cy,
                    random.uniform(-10, 10), random.uniform(-30, -5),
                    life=random.uniform(0.8, 1.2),
                    col=(80, 80, 95), size=2, grav=-6.0, fade=True
                ))

            destroyed = True

        elif shot_idx == 4:
            # (4) FLASH → Bedroom. Calm interior, hero sits up.
            # Build the interior each frame
            room, bed, pillow = draw_bedroom(world, base_y)
            # Camera: static inside room with gentle zoom out
            p = ease_in_out(shot_t / SHOT_DUR[4])
            cam.set(
                cx=room.centerx,
                cy=room.centery + 8,
                zoom=lerp(1.15, 1.0, p),
            )
            # Hero in bed → sit up animation
            # Use a simple vertical tween for the torso rectangle
            torso_h = int(lerp(6, 10, p))
            hero_bed_x = bed.x + 28
            hero_bed_y = bed.y + 2
            pygame.draw.rect(world, (90, 200, 255), (hero_bed_x, hero_bed_y - torso_h, 8, torso_h))
            world.set_at((hero_bed_x + 4, hero_bed_y - torso_h + 2), WHITE)

            # residual flash fades out quickly
            if flash > 0:
                flash = max(0, flash - 900 * dt)

        else:
            # (5) Walk outside: the town is safe (relief)
            p = ease_in_out(shot_t / SHOT_DUR[5])
            draw_buildings(world, b_surfs, b_rects, destroyed=False)
            draw_people(world, b_rects, total_frames / FPS, lead_pos=None)

            # Hero steps out of house and looks around
            out_x = int(lerp(b_rects[0].centerx, b_rects[1].centerx - 30, p))
            out_y = hero_y
            pygame.draw.rect(world, (90, 200, 255), (out_x - 4, out_y - 10, 8, 10))
            world.set_at((out_x, out_y - 8), WHITE)

            # Camera pulls back to a reassuring wide
            cam.set(
                cx=int(lerp(b_rects[0].centerx, (b_rects[0].centerx + b_rects[2].centerx)//2, p)),
                cy=int(lerp(base_y - 40, base_y - vh//3, p)),
                zoom=lerp(1.0, 0.95, p),
            )

            # Soft “It was only a dream…” caption near bottom
            font = pygame.font.Font(None, 16)
            cap = font.render("…just a dream.", False, (220, 220, 230))
            world.blit(cap, (b_rects[1].centerx - cap.get_width()//2, base_y - 22))

        # Update particles (shared across shots)
        for pr in particles[:]:
            pr.update(dt)
            if pr.life <= 0:
                particles.remove(pr)

        # Draw particles ON TOP of world where appropriate
        for pr in particles:
            pr.draw(world)

        # Present camera crop
        cam.present(world, surf)

        # Overlays
        draw_letterbox(surf, LETTERBOX if shot_idx != 5 else int(lerp(LETTERBOX, 0, ease_in_out(shot_t / SHOT_DUR[5]))))
        if fade_in > 0:
            fade_in = max(0, fade_in - 360 * dt)
            draw_fade(surf, fade_in)
        if fade_out > 0:
            fade_out = max(0, fade_out - 360 * dt)
            draw_fade(surf, fade_out)
        if flash > 0:
            draw_flash(surf, flash)

        # Tiny corner “Press a key to skip” for first few shots
        if shot_idx <= 2:
            font = pygame.font.Font(None, 12)
            hint = font.render("Press any key to skip", False, (200, 200, 210))
            surf.blit(hint, (vw - hint.get_width() - 4, vh - LETTERBOX - 12))

        # Scale to window
        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()

    # End of cinematic.
    # Optional final title card fade-in (briefly)
    end_t = 0.0
    while end_t < 1.0:
        dt = clock.tick(FPS) / 1000.0
        end_t += dt
        # reuse last safe town frame as backdrop
        world.fill((0,0,0,0))
        draw_vgradient(world, SKY_MORN_TOP, SKY_MORN_BOT)
        draw_ground(world, base_y)
        draw_buildings(world, b_surfs, b_rects, destroyed=False)
        cam.set(cx=(b_rects[0].centerx + b_rects[2].centerx)//2, cy=base_y - vh//3, zoom=0.95)
        cam.present(world, surf)
        draw_letterbox(surf, 0)
        title = pygame.font.Font(None, 28).render("PIXEL ADVENTURES", False, TITLE_COL)
        surf.blit(title, ((vw - title.get_width())//2, 10))
        draw_fade(surf, int(lerp(255, 0, end_t)))
        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                return
