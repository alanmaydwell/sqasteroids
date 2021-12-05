#!/usr/bin/env python3
"""
Pygame siple animatin practice.
Move a surface accross a window using blit.
"""


import pygame
pygame.init()

# Window and caption
screen = pygame.display.set_mode((800, 512))
pygame.display.set_caption("Hoopy")
# for framerate limit
clock = pygame.time.Clock()
# Samll surface to move accross the screen
spuddle = pygame.Surface((16, 100))
spuddle.fill("Red")
spud_x = 0


while True:
    # Getting close window icon to actually close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
    # Animation
    screen.fill((0, 0, 0))
    screen.blit(spuddle, (spud_x, 0))
    spud_x += 1
    if spud_x > 810:
        spud_x = -10
    pygame.display.update()
    # Max framerate
    clock.tick(60)
