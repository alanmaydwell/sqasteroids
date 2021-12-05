#!/usr/bin/env python3

"""
Pygame animation practice
Using blit and surfaces (not Pygame sprites)
Moving things and scrolling lined background
"""

import pygame
pygame.init()

WIDTH = 800
HEIGHT = 600

class Movable:
    """Movable surface - simple homemade sprite"""
    def __init__(self, x=0, y=0, width=16, height=12, dx=4, dy=3, colour=(255, 255, 255)):
        # Could switch to using pygame.Rect to store position
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.fill(colour)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.confine()

    def confine(self):
        """Confine coordinates within the allowed range"""
        self.x, self.dx = confiner(self.x, self.dx, minimum=0, maximum=WIDTH-self.width)
        self.y, self.dy = confiner(self.y, self.dy, minimum=0, maximum=HEIGHT-self.height)


class GameThing:
    """Set window with some moving things within it"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Things Moving")
        self.frameclock = pygame.time.Clock()


        # Vertical lines for scrolling background
        self.lined_img = pygame.Surface((WIDTH, HEIGHT))
        for x in range(0, WIDTH, 32):
            pygame.draw.line(self.lined_img, (0, 0, 255), (x, 0), (x, HEIGHT))

        # Single block
        self.block_img = Movable(x=100, width=48, height=32, dx=-1)

        # Several trailing blocks
        self.movables = [Movable(v*2, v, colour=(128, 0, 200)) for v in range(10, 320, 10)]

        self.in_progress = True
        self.do_animation()

    def do_animation(self):
        loopcount = 0
        while self.in_progress:
            self.screen.fill((0, 0, 0))
            self.check_events()

            self.screen.blit(self.lined_img, (-loopcount%32, 0))

            self.screen.blit(self.block_img.surface, (self.block_img.x, self.block_img.y))
            self.block_img.update()

            for movable in self.movables:
                self.screen.blit(movable.surface, (movable.x, movable.y))
                movable.update()

            pygame.display.update()
            self.frameclock.tick(60)
            loopcount += 1
        pygame.quit()

    def check_events(self):
        """Enable exit if ESCAPE pressed or close window icon clicked"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                             and event.key == pygame.K_ESCAPE):
                self.in_progress = False


def confiner(current, delta, minimum, maximum, bounce=False):
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
