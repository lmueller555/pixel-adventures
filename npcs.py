import pygame
import random

ICON_W, ICON_H = 16, 24


def _simple_sprite(skin, hair, outfit, frame):
    s = pygame.Surface((ICON_W, ICON_H), pygame.SRCALPHA)
    pygame.draw.rect(s, hair, (4, 0, 8, 4))
    pygame.draw.rect(s, skin, (4, 4, 8, 4))
    pygame.draw.rect(s, outfit, (3, 8, 10, 8))
    pygame.draw.rect(s, (0, 0, 0), (3, 8, 10, 8), 1)
    ly, ry = (16, 18) if frame % 2 else (18, 16)
    pygame.draw.rect(s, outfit, (4, ly, 4, 6))
    pygame.draw.rect(s, outfit, (8, ry, 4, 6))
    return s

SKIN = (255, 224, 189)

SPRITES = {
    "male": [_simple_sprite(SKIN, (80, 50, 20), (60, 80, 180), f) for f in (0, 1)],
    "female": [_simple_sprite(SKIN, (240, 200, 80), (200, 80, 120), f) for f in (0, 1)],
    "innkeeper": [_simple_sprite(SKIN, (90, 50, 20), (40, 160, 40), f) for f in (0, 1)],
    "shopkeeper": [_simple_sprite(SKIN, (30, 30, 30), (160, 140, 60), f) for f in (0, 1)],
}


def sprite(kind, frame=0):
    return SPRITES[kind][frame % 2]


class NPC:
    def __init__(self, pos, kind="male", radius=40, speed=20):
        self.rect = pygame.Rect(pos[0], pos[1], 8, 8)
        self.kind = kind
        self.frames = SPRITES[kind]
        self.anchor = pygame.Vector2(pos)
        self.radius = radius
        self.speed = speed
        self.dir = pygame.Vector2(0, 0)
        self.change = 0.0
        self.anim_t = 0.0
        self.frame = 0

    def update(self, dt, obstacles, bounds):
        self.change -= dt
        if self.change <= 0:
            self.change = random.uniform(1.0, 3.0)
            self.dir = pygame.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
            if self.dir.length_squared() > 0:
                self.dir = self.dir.normalize()
        move = self.dir * self.speed * dt
        self.rect.x += int(round(move.x))
        for o in obstacles:
            if self.rect.colliderect(o):
                if move.x > 0:
                    self.rect.right = o.left
                elif move.x < 0:
                    self.rect.left = o.right
        self.rect.y += int(round(move.y))
        for o in obstacles:
            if self.rect.colliderect(o):
                if move.y > 0:
                    self.rect.bottom = o.top
                elif move.y < 0:
                    self.rect.top = o.bottom
        self.rect.clamp_ip(bounds)
        offset = pygame.Vector2(self.rect.center) - self.anchor
        if offset.length() > self.radius:
            offset.scale_to_length(self.radius)
            self.rect.center = (int(self.anchor.x + offset.x), int(self.anchor.y + offset.y))
        if self.dir.length_squared() > 0:
            self.anim_t += dt * 4
            self.frame = int(self.anim_t) % 2
        else:
            self.anim_t = 0.0
            self.frame = 0

    def draw(self, surf, offset):
        sp = self.frames[self.frame]
        rect = sp.get_rect(midbottom=(self.rect.centerx - offset[0], self.rect.bottom - offset[1]))
        surf.blit(sp, rect)
