import pygame
import class_select


def _player_sprite_for(cid, color):
    return class_select._class_icon(cid, color)

def run(screen, clock, virtual_size):
    vw, vh = virtual_size
    surf = pygame.Surface(virtual_size)

    knight = _player_sprite_for("knight", class_select.CLASSES[0]["color"])
    black = _player_sprite_for("black_mage", class_select.CLASSES[1]["color"])
    white = _player_sprite_for("white_mage", class_select.CLASSES[2]["color"])

    k_rect = knight.get_rect(midbottom=(-20, vh-40))
    b_rect = black.get_rect(midbottom=(vw-40, vh-40))
    w_rect = white.get_rect(midbottom=(vw+20, vh-40))

    fireball = None
    fire_step = pygame.Vector2(0,0)
    slash_timer = 0
    explosion_timer = 0
    heal_timer = 0

    frame = 0
    while frame < 300:
        dt = clock.tick(60)/1000.0
        frame += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    return

        # sequence
        if frame < 60:
            k_rect.x = -20 + int(frame * (100/60))
        elif frame == 60:
            slash_timer = 15
        elif frame == 120:
            fireball = pygame.Rect(b_rect.left-4, b_rect.centery-2, 4,4)
            diff = pygame.Vector2(k_rect.center) - pygame.Vector2(fireball.center)
            fire_step = diff / 40
        elif 120 < frame <= 160 and fireball:
            fireball.x += int(fire_step.x)
            fireball.y += int(fire_step.y)
            if fireball.colliderect(k_rect):
                fireball = None
                explosion_timer = 20
        elif frame == 160:
            heal_timer = 0
            w_rect.x = vw+20
        elif 160 <= frame < 200:
            w_rect.x -= 2
            if w_rect.x <= k_rect.x + 40:
                w_rect.x = k_rect.x + 40
        elif frame == 200:
            heal_timer = 40
        if heal_timer > 0:
            heal_timer -= 1
        if slash_timer > 0:
            slash_timer -= 1
        if explosion_timer > 0:
            explosion_timer -= 1

        # draw
        surf.fill((12,12,18))
        # ground line
        pygame.draw.line(surf, (60,60,90), (0, vh-32), (vw, vh-32))

        surf.blit(knight, k_rect)
        surf.blit(black, b_rect)
        surf.blit(white, w_rect)

        if fireball:
            pygame.draw.rect(surf, (255,140,40), fireball)
            surf.set_at(fireball.center, (255,255,190))
        if slash_timer > 0:
            slash = pygame.Rect(k_rect.right, k_rect.centery-4, 12,8)
            pygame.draw.rect(surf, class_select.CLASSES[0]["color"], slash)
        if explosion_timer > 0:
            ex = pygame.Rect(k_rect.centerx-6, k_rect.centery-6, 12,12)
            pygame.draw.rect(surf, (255,180,60), ex)
        if heal_timer > 0:
            hx, hy = k_rect.centerx, k_rect.top-10
            pygame.draw.line(surf, class_select.CLASSES[2]["color"], (hx-3, hy), (hx+3, hy))
            pygame.draw.line(surf, class_select.CLASSES[2]["color"], (hx, hy-3), (hx, hy+3))

        pygame.transform.scale(surf, screen.get_size(), screen)
        pygame.display.flip()
