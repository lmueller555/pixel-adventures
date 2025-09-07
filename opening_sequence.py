import pygame
import random
import buildings as bld


def _charred_surface(src: pygame.Surface) -> pygame.Surface:
    """Return a darkened version of a building surface."""
    s = src.copy()
    overlay = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    overlay.fill((30, 30, 30, 200))
    s.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return s


def run(screen, clock, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    # Buildings of Odelia (three samples across the screen)
    b_surfs = [bld.House().surface, bld.Inn().surface, bld.ItemShop().surface]
    b_rects = [
        b_surfs[0].get_rect(midbottom=(vw // 2 - 80, vh - 32)),
        b_surfs[1].get_rect(midbottom=(vw // 2, vh - 32)),
        b_surfs[2].get_rect(midbottom=(vw // 2 + 80, vh - 32)),
    ]
    charred = [_charred_surface(s) for s in b_surfs]

    meteor = pygame.Rect(vw // 2 - 8, -16, 16, 16)
    meteor_speed = 300
    impact_y = vh - 32 - b_surfs[1].get_height()

    explosion_timer = 0
    destroyed = False
    flames = []  # each flame is [rect, timer]

    frame = 0
    while frame < 240:
        dt = clock.tick(60) / 1000.0
        frame += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_z,
                pygame.K_SPACE,
            ):
                return

        if not destroyed:
            meteor.y += int(meteor_speed * dt)
            if meteor.y >= impact_y:
                meteor.y = impact_y
                destroyed = True
                explosion_timer = 30
        else:
            # Spawn flames randomly on charred buildings
            if random.random() < 0.3:
                b = random.choice(b_rects)
                r = pygame.Rect(
                    random.randint(b.left, b.right - 6),
                    random.randint(b.top, b.bottom - 10),
                    6,
                    10,
                )
                flames.append([r, random.randint(20, 40)])
            # Update flames
            for fl in flames:
                fl[0].y += random.randint(-1, 1)
                fl[1] -= 1
            flames = [f for f in flames if f[1] > 0]
            if explosion_timer > 0:
                explosion_timer -= 1

        # Draw
        surf.fill((12, 12, 18))
        pygame.draw.line(surf, (60, 60, 90), (0, vh - 32), (vw, vh - 32))

        if destroyed:
            for s, r in zip(charred, b_rects):
                surf.blit(s, r)
        else:
            for s, r in zip(b_surfs, b_rects):
                surf.blit(s, r)

        if not destroyed or explosion_timer > 0:
            pygame.draw.ellipse(surf, (220, 220, 80), meteor)

        if explosion_timer > 0:
            radius = (30 - explosion_timer) * 3
            pygame.draw.circle(
                surf,
                (255, 180, 60),
                (meteor.centerx, meteor.bottom),
                radius,
            )

        for r, _ in flames:
            pygame.draw.rect(surf, (255, 120, 0), r)
            inner = r.inflate(-2, -2)
            pygame.draw.rect(surf, (255, 220, 160), inner)

        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()

