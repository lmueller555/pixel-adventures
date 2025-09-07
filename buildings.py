import pygame

class Building:
    """Base building with common geometry and door/solid rectangles."""
    size = (60, 60)

    def __init__(self):
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        w, h = self.size
        # Door area for interaction (lower 8 pixels of actual door)
        self.door = pygame.Rect(w // 2 - 8, h - 8, 16, 8)
        # Solid portion (exclude bottom 8 pixels to allow standing in doorway)
        self.solid = pygame.Rect(0, 0, w, h - 8)
        self._draw()

    def _draw(self):
        raise NotImplementedError


class House(Building):
    def _draw(self):
        s = self.surface
        w, h = self.size
        # Roof
        pygame.draw.polygon(s, (160, 40, 40), [(0, 20), (w // 2, 0), (w, 20)])
        pygame.draw.line(s, (80, 20, 20), (0, 20), (w, 20))
        # Walls
        pygame.draw.rect(s, (210, 180, 140), (0, 20, w, h - 20))
        pygame.draw.rect(s, (80, 40, 20), (0, 20, w, h - 20), 2)
        # Door
        pygame.draw.rect(s, (120, 80, 40), (w // 2 - 8, h - 20, 16, 20))
        pygame.draw.rect(s, (60, 30, 0), (w // 2 - 8, h - 20, 16, 20), 2)
        # Windows
        for x in (10, w - 22):
            pygame.draw.rect(s, (220, 220, 255), (x, 32, 12, 12))
            pygame.draw.rect(s, (60, 30, 0), (x, 32, 12, 12), 2)
            pygame.draw.line(s, (60, 30, 0), (x + 6, 32), (x + 6, 44))
            pygame.draw.line(s, (60, 30, 0), (x, 38), (x + 12, 38))


class Inn(Building):
    def _draw(self):
        s = self.surface
        w, h = self.size
        # Roof
        pygame.draw.polygon(s, (80, 80, 160), [(0, 20), (w // 2, 0), (w, 20)])
        pygame.draw.line(s, (40, 40, 90), (0, 20), (w, 20))
        # Walls
        pygame.draw.rect(s, (190, 150, 100), (0, 20, w, h - 20))
        pygame.draw.rect(s, (80, 40, 20), (0, 20, w, h - 20), 2)
        # Door
        pygame.draw.rect(s, (110, 70, 40), (w // 2 - 10, h - 20, 20, 20))
        pygame.draw.rect(s, (60, 30, 0), (w // 2 - 10, h - 20, 20, 20), 2)
        # Upper windows
        for x in (8, w // 2 - 6, w - 20):
            pygame.draw.rect(s, (230, 230, 255), (x, 32, 12, 12))
            pygame.draw.rect(s, (60, 30, 0), (x, 32, 12, 12), 2)
            pygame.draw.line(s, (60, 30, 0), (x + 6, 32), (x + 6, 44))
            pygame.draw.line(s, (60, 30, 0), (x, 38), (x + 12, 38))
        # Sign
        pygame.draw.rect(s, (200, 200, 120), (w // 2 - 15, 46, 30, 10))
        pygame.draw.rect(s, (80, 60, 20), (w // 2 - 15, 46, 30, 10), 2)
        # Draw INN text using simple lines
        base_x = w // 2 - 11
        pygame.draw.line(s, (80, 60, 20), (base_x, 48), (base_x, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 6, 48), (base_x + 6, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 6, 48), (base_x + 10, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 10, 48), (base_x + 10, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 12, 48), (base_x + 12, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 18, 48), (base_x + 18, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 18, 48), (base_x + 22, 52))
        pygame.draw.line(s, (80, 60, 20), (base_x + 22, 48), (base_x + 22, 52))


class ItemShop(Building):
    def _draw(self):
        s = self.surface
        w, h = self.size
        # Roof
        pygame.draw.polygon(s, (60, 120, 60), [(0, 20), (w // 2, 0), (w, 20)])
        pygame.draw.line(s, (30, 80, 30), (0, 20), (w, 20))
        # Walls
        pygame.draw.rect(s, (200, 170, 130), (0, 20, w, h - 20))
        pygame.draw.rect(s, (80, 40, 20), (0, 20, w, h - 20), 2)
        # Door
        pygame.draw.rect(s, (120, 80, 40), (w // 2 - 8, h - 20, 16, 20))
        pygame.draw.rect(s, (60, 30, 0), (w // 2 - 8, h - 20, 16, 20), 2)
        # Display window
        pygame.draw.rect(s, (180, 220, 220), (10, 36, w - 20, 16))
        pygame.draw.rect(s, (60, 30, 0), (10, 36, w - 20, 16), 2)
        # Sign
        pygame.draw.rect(s, (150, 100, 50), (w // 2 - 20, 24, 40, 10))
        pygame.draw.rect(s, (60, 30, 0), (w // 2 - 20, 24, 40, 10), 2)
        base_x = w // 2 - 18
        # Draw SHOP text (simplified)
        pygame.draw.line(s, (255, 255, 255), (base_x, 26), (base_x + 8, 26))
        pygame.draw.line(s, (255, 255, 255), (base_x, 30), (base_x + 8, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x, 26), (base_x, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 4, 26), (base_x + 4, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 8, 26), (base_x + 8, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 12, 26), (base_x + 12, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 16, 26), (base_x + 16, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 20, 26), (base_x + 24, 26))
        pygame.draw.line(s, (255, 255, 255), (base_x + 20, 30), (base_x + 24, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 24, 26), (base_x + 24, 30))
        pygame.draw.line(s, (255, 255, 255), (base_x + 20, 30), (base_x + 20, 34))
