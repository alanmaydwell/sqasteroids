#!/usr/bin/env python3

"""
Pygame animation practice
Using Pygame sprites and handy associated sprite group container.
"""


import pygame
pygame.init()

WIDTH = 1280
HEIGHT = 720

class Sprite(pygame.sprite.Sprite):
    """Subclass of Pygame sprite"""
    def __init__(self, x=0, y=0, dx=0, dy=0, colour=(255, 255, 0), height=64, width=64, angle=0):
        super().__init__()
        self.dx = dx
        self.image = pygame.Surface([width, height])
        self.image.fill(colour)
        self.image.set_colorkey((0, 0, 0))
        # Trying transparency
        self.image.set_alpha(96)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        if angle:
            self.rotate(angle)

    def rotate(self, angle=0):
        """Rotate sprite by given angle
        Params:
            angle - rotation angle in degrees (float/int)
        """
        original_centre = self.rect.center
        self.image = pygame.transform.rotate(self.image, angle)
        # Need to reset the rectangle - it's always parallel to screen axes
        # so size will usually change when image is rotated
        self.rect = self.image.get_rect()
        # Ensure new rect has same centre position as the previous one
        self.rect.center = original_centre

    def update(self):
        """Update position - currently just in x direction"""
        self.rect.x += self.dx
        if self.rect.x > WIDTH:
            self.rect.x = -self.rect.width


if __name__ == "__main__":
    # Setup animation
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Create sprite group and populate it with sprites
    all_sprites = pygame.sprite.Group()
    for i in range(40):
        all_sprites.add(Sprite(x=-16*i, y=16*i, dx=1))
        all_sprites.add(Sprite(x=(-16*i)-64, y=16*i, dx=2, colour=(255, 255, 128), angle=20))
        all_sprites.add(Sprite(x=(-16*i)-128, y=16*i, dx=3, colour=(0, 255, 255)))
        all_sprites.add(Sprite(x=(-16*i)-196, y=16*i, dx=4, colour=(255, 0, 255)))

    # Animation loop
    while True:
        # Event Handling - close window when icon clicked
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

        # Clear the screen
        screen.fill((0, 0, 0))
        # Draw sprite group (to background screen)
        all_sprites.draw(screen)
        # Update foreground screen from background
        pygame.display.update()
        # Update sprite positions - for whole group
        all_sprites.update()
        # Max framerate
        clock.tick(120)
