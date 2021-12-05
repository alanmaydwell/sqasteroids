#!/usr/bin/env python3

"""
Pygame animation practice
Using blit and surfaces (not Pygame sprites)
Various things moving around the window with different colours that are
transparent and blend upon overlap.
"""


import random
import pygame
pygame.init()

WIDTH = 1280
HEIGHT = 800

class Movable:
    """Movable surface - simple homemade sprite"""
    def __init__(self, x=0, y=3, width=48, height=48, dx=4, dy=3, colour=(255, 255, 255)):
        self.dx, self.dy = dx, dy
        self.surface = pygame.Surface((width, height))
        self.rect = self.surface.get_rect()
        self.rect.center = (x, y)
        self.surface.fill(colour)
        # Transparency
        self.surface.set_alpha(64)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.confine()

    def confine(self):
        """Confine coordinates within the allowed range"""
        self.rect.centerx, self.dx = confiner(self.rect.centerx, self.dx, minimum=0, maximum=WIDTH)
        self.rect.centery, self.dy = confiner(self.rect.centery, self.dy, minimum=0, maximum=HEIGHT)


class GameThing:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Things Moving With Transparency")
        self.frameclock = pygame.time.Clock()

        # A trail of shapes
        self.movables = [Movable(v*2, v, colour=(128, 0, 200)) for v in range(0, 640, 10)]

        # Some random rectangles with random position and speed
        for _ in range(32):
            dx = dy = 0
            while dx + dy == 0:
                dx = random.randint(-3, 4)
                dy = random.randint(-3, 4)
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            colour = random.choice([(255, 255, 0), (0, 255, 255), (255, 0, 0),
                                    (0, 255, 0), (0, 0, 255)])
            self.movables.append(Movable(x, y, 160, 160, dx, dy, colour=colour))

        self.in_progress = True
        self.do_animation()

    def do_animation(self):
        loopcount = 0
        while self.in_progress:
            self.screen.fill((0, 0, 0))
            self.check_events()

            for movable in self.movables:
                self.screen.blit(movable.surface, (movable.rect.topleft))
                movable.update()

            pygame.display.update()
            self.frameclock.tick(120)
            loopcount += 1
        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                             and event.key == pygame.K_ESCAPE):
                self.in_progress = False


def confiner(current, delta, minimum, maximum, bounce=True):
    """Confine value between maximum and minumum allowed
    Intended for moving objects on screen. Either bounce
    or wrap-round possible.
    Args:
        current - the current value
        delta - the current value increment
        minimum - the minimum allowed value
        maximum - the maximum allowed value
        bounce (bool) - when true cause value to "rebound" otherwise wrap beteen min and max

    Returns:
        new values for position and delta
    """
    # Only do something if current value not betwen its minium or maximum
    if not minimum <= current <= maximum:
        if bounce:
            # Reset current to either the miniumum or maximum and invert delta to cause a bounce
            current = minimum*(current < minimum) + maximum*(current > maximum)
            delta = -delta
        else:
            # Wrap - shift coordinate between min and max. No need to invert delta here.
            current = maximum*(current < minimum) + minimum*(current > maximum)
    return current, delta


if __name__ == "__main__":
    go = GameThing()
