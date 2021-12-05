#!/usr/bin/env python3

"""
Asteroids style game
"""

# To do -

#  Hi score
#  Collisions with ship
# Abolish game_in_progress and use level > 0 instead

import math
import random
import pygame
pygame.init()

WIDTH = 1280
HEIGHT = 800
MIDWIDTH = WIDTH * 0.5
MIDHEIGHT = HEIGHT * 0.5
XSCALE = WIDTH/40
YSCALE = HEIGHT/25
XCHUNKS = list(range(0, WIDTH, int(XSCALE)))
YCHUNKS = list(range(0, HEIGHT, int(YSCALE)))


class RectSprite(pygame.sprite.Sprite):
    """Sprite
    Either uses supplied image or creates a rectangle of specified sie
    """
    def __init__(self, x=0, y=0, dx=0, dy=0, image=None, width=64, height=64,
                 colour=(255, 255, 255), angle=0, alpha=255, life=80, dlife=0):
        super().__init__()
        self.dx = dx
        self.dy = dy
        self.life = life
        self.dlife = dlife

        if image:
            self.image = image
        else:
            self.image = pygame.Surface([width, height])
            self.image.fill(colour)

        self.image.set_colorkey((0, 0, 0))
        self.image.set_alpha(alpha)
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
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.life += self.dlife
        if self.life < 0:
            self.kill()
        self.confine()

    def confine(self):
        """Confine coordinates within the allowed range"""
        self.rect.centerx, self.dx = confiner(self.rect.centerx, self.dx, minimum=0, maximum=WIDTH)
        self.rect.centery, self.dy = confiner(self.rect.centery, self.dy, minimum=0, maximum=HEIGHT)


class PlayerSprite(RectSprite):
    def __init__(self, *args, **kwargs):
        """
        Subclass for player sprite with extra handling for rotations, accelleration
        and bullet direction
        """
        super().__init__(*args, **kwargs)
        self.orientation = 0
        self.make_rotations()
        self.last_orient = len(self.rotated_images)
        self.bullet_dx = 0
        self.bullet_dy = -8

    def make_rotations(self, steps=36):
        self.rotated_images = []
        for orientation in range(steps):
            dangle = 360 * orientation/steps
            rangle = 2 * math.pi * orientation/steps
            rotimage = pygame.transform.rotate(self.image, dangle)
            self.rotated_images.append([dangle, rangle, rotimage])

    def spin(self, step):
        """Rotate the ship when orientation changed
        Also updates the sprite's rectangle to suit new angle
        Args
            step - amount to change the orientation (by position)
            positive/negative - clockwise/anticlockwise
        """
        self.orientation = (self.orientation +  step) % self.last_orient
        original_centre = self.rect.center
        self.image = self.rotated_images[self.orientation][2]
        self.rect = self.image.get_rect()
        self.rect.center = original_centre
        #Bullet launch speed
        rangle = self.rotated_images[self.orientation][1]
        self.bullet_dx = -8 * math.sin(rangle)
        self.bullet_dy = -8 * math.cos(rangle)

    def accellerate(self):
        rangle = self.rotated_images[self.orientation][1]
        self.dx -= 1 * math.sin(rangle)
        self.dy -= 1 * math.cos(rangle)
        # Friction at high speeds - stop going too fast
        if self.dx * self.dx > 100:
            self.dx *= 0.9
        if self.dy * self.dy > 100:
            self.dy *= 0.9

class TextSprite(pygame.sprite.Sprite):
    """Used to display text"""
    def __init__(self, x=0, y=0, text="", font=None, size=36, colour=(255, 255, 255)):
        super().__init__()
        font = pygame.font.SysFont(font, size)
        self.image = font.render(text, True, colour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Things Happening")
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.square_sprites = pygame.sprite.Group()
        self.player_bullet_sprites = pygame.sprite.Group()
        self.keep_going = True
        self.game_in_progress = False
        self.level = 0 # Could replace game_in_progress with level > 0
        self.score = 0

        # Player ship setup
        player_ship_image = pygame.Surface([20, 32])
        pygame.draw.polygon(player_ship_image, (255, 255, 0), [(0,32), (10, 0), (20, 32), (10, 24)], width=0)
        self.player = PlayerSprite(MIDWIDTH, MIDHEIGHT, 0, 0, image=player_ship_image)
        # Used to control player fire rate
        self.reload_counter = 0

        self.game_loop()


    def welcome_screen(self):
        # Decorative jumping up and down squares
        for yi, y in enumerate(YCHUNKS[-9:]): # Last 7 ychunks
            for xi, x in enumerate(XCHUNKS):
                if xi%2 == 0:
                    sprite = RectSprite(x=x, y=y, dy=-4, width=int(XSCALE), height=int(YSCALE), colour=(yi*20, 0, 255-(yi*20)), alpha=180)
                    self.all_sprites.add(sprite)
                else:
                    sprite = RectSprite(x=x, y=y, dy=-2, width=int(XSCALE), height=int(YSCALE), colour=(yi*22, 255-(yi*20),0), alpha=180)
                    self.all_sprites.add(sprite)

        # Information Text
        text = ["SQASTEROIDS!!!",
                "",
                "",
                "",
                "Controls",
                "A - rotate one way",
                "D - rotate another way",
                "Right Shift - thrust",
                "Enter - fire",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Press SPACE to start"
                ]
        for wi, line in enumerate(text):
            if line:
                cval = 255 - 10*wi
                colour = (255, 255, cval)
                sprite = TextSprite(text=line, y = YCHUNKS[wi+3], colour=colour)
                sprite.rect.centerx = MIDWIDTH
                self.all_sprites.add(sprite)

    def start_game(self):
        self.game_in_progress = True
        self.score = 0
        self.level = 1
        # Empty the sprite groups - clear any leftovers from previous game
        self.all_sprites.empty()
        self.square_sprites.empty()
        self.player_bullet_sprites.empty()
        self.level_setup()
        self.all_sprites.add(self.player)

    def level_setup(self):
        # Squasteroids
        for _ in range(3 + self.level):
            # Set starting positions
            x = MIDWIDTH
            y = MIDHEIGHT
            # keep middle of screen clear as a safe zone for ship at level start
            while (XCHUNKS[10] < x < XCHUNKS[-10] and YCHUNKS[10] < y < YCHUNKS[-10]):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
            self.make_sqasteroid(x, y, life=3)

    def make_sqasteroid(self, x, y, life=3):
        angle = random.uniform(0, math.pi*2)
        dx = 4 * math.sin(angle)
        dy = 4 * math.cos(angle)
        new_square = RectSprite(x, y, dx, dy, width=int(XSCALE*life), height=(YSCALE*life), colour=(100, 50, 200), alpha=128, life=life, dlife=0)
        self.all_sprites.add(new_square)
        self.square_sprites.add(new_square)

    def shoot(self):
        """Shoot bullet"""
        if self.reload_counter < 1:
            self.reload_counter = 15
            shot = RectSprite(self.player.rect.centerx, self.player.rect.centery,
                              self.player.bullet_dx+self.player.dx,
                              self.player.bullet_dy+self.player.dy,
                              width=2, height=2, life=80, dlife=-1)
            self.all_sprites.add(shot)
            self.player_bullet_sprites.add(shot)

    def bullet_collisions(self):
        # Bullet/square collision - removes any that have collided from the groups
        # Note this does not delete the sprites themselves - just ends their membership of *any* groups
        collided = pygame.sprite.groupcollide(self.square_sprites, self.player_bullet_sprites, True, True)
        for target in collided.keys():
            # Increase score, with bigger score from smaller target
            self.score += (4-target.life)
            #Make 2 smaller asteroids if destroyed asteroid is above minimum size
            if target.life > 1:
                life = target.life -1
                self.make_sqasteroid(target.rect.x, target.rect.y, life=life)
                self.make_sqasteroid(target.rect.x, target.rect.y, life=life)
            # Add explosion here
            for dx, dy in [(6, 6), (-6, 6), (6, -6), (-6, -6), (8, 0), (-8, 0), (0, 8), (0, -8)]:
                self.all_sprites.add(RectSprite(target.rect.centerx,
                                                target.rect.centery,
                                                dx, dy, width=7, height=7,
                                                colour=(100, 50, 200), dlife=-5))

    def game_loop(self):
        font = pygame.font.SysFont(None, 36)
        self.welcome_screen()
        while self.keep_going:
            self.check_events()
            self.screen.fill((0, 0, 0))

            self.reload_counter -= 1
            self.all_sprites.draw(self.screen)
            self.bullet_collisions()
            self.all_sprites.update()

            # When game in progress
            if self.level > 0:
                # Display
                score_image = font.render(f"SCORE: {self.score}", True, (0, 255, 0))
                level_image = font.render(f"LEVEL: {self.level}", True, (0, 255, 0))
                self.screen.blit(score_image, (XCHUNKS[1], YCHUNKS[0]))
                self.screen.blit(level_image, (XCHUNKS[-4], YCHUNKS[0]))

                # New Level when all enemies destroyed
                if len(self.square_sprites) < 1:
                    self.level += 1
                    self.level_setup()

            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                             and event.key == pygame.K_ESCAPE):
                self.keep_going = False
        # Player Controls
        keys = pygame.key.get_pressed()
        # Rotate clockwise
        if keys[pygame.K_a]:
            self.player.spin(1)
        # Rotate anticlockwise
        if keys[pygame.K_d]:
            self.player.spin(-1)
        # Accellerate
        if keys[pygame.K_RSHIFT]:
            self.player.accellerate()
        # Shoot
        if keys[pygame.K_RETURN]:
            self.shoot()

        if not self.game_in_progress and keys[pygame.K_SPACE]:
            self.start_game()


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
            current = minimum * (current < minimum) + maximum * (current > maximum)
            delta = -delta
        else:
            # Wrap - shift coordinate between min and max. No need to invert delta here.
            current = maximum * (current < minimum) + minimum * (current > maximum)
    return current, delta


if __name__ == "__main__":
    go = Game()
