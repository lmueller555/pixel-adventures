# main.py
# Pixel Adventures — Flow: Title -> Class Select -> Odelia -> Title

import sys
import pygame
import title_screen
import class_select
import opening_sequence
import odelia

VIRTUAL_SIZE = title_screen.VIRTUAL_SIZE
CAPTION = "Pixel Adventures"

def main():
    pygame.init()
    pygame.display.set_caption(CAPTION)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    while True:
        # Title
        r = title_screen.run(screen, clock, VIRTUAL_SIZE)
        if r == "quit":
            break

        # Class Select
        choice = class_select.run(screen, clock, VIRTUAL_SIZE)
        if choice in ("quit", "back"):
            if choice == "quit":
                break
            else:
                continue

        # Opening sequence (battle/introduction)
        opening_sequence.run(screen, clock, VIRTUAL_SIZE)

        # Odelia town
        r = odelia.run(screen, clock, choice, VIRTUAL_SIZE)
        if r == "quit":
            break
        # if "title", loop restarts at title

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
