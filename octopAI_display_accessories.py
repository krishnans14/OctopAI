"""
This python file would be a place for all the classes and functions that are required to make 
the display work for the OctopAI.py file
"""

import pygame
import os
import random


WIN_WIDTH = 648
WIN_HEIGHT = 868

STAT_FONT = pygame.font.SysFont("comicsans", 50)

OCT_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "oct1.png"))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("images", "oct2.png")))]

OBSTACLE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "obstacle.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base_half.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "background.png")))


class Octopus:
    """
    This is the octopus class whose motions are trained using the AI.
    Technically, the octopus is stationary and the base and the obstacles move
    (but I pretend that this is not the case).

    When the octopus jumps, that is, to go down (or go up), it has a change in velocity
    to indicate that.

    The simulated movement of the octopus is computed using the Newton's law of motions
    assuming an acceleration of 3 m/s2.

    The movement simulation, based on whether the jump results in going up or down,
    will also tilt the octopus image so as to look like it is jumping head down.

    """

    IMGS = OCT_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x;
        self.y = y;
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #negative because of the y direction and going up is the negative velocity
        self.tick_count = 0 # when we last jumped. So that physics formulas know that
        self.height = self.y

    def move(self): #to move every single frame to move
        self.tick_count += 1

        # Newton's law of motion to compute displacement
        d = self.vel*self.tick_count + 1.5*self.tick_count**2 # S = ut + 1/2 a t^2

        if d >= 16:
            d = 16
        if d <0:
            d -= 2

        self.y = self.y + d

        # moving upwards to give a slight bit of tilt up
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: # nose diving
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL


    def draw(self, win):
        self.img_count += 1 # To track how many time ticks have passed

        # To show the moving of octopus through changing the image being shown
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*5:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*5+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When octopus is diving
        if self.tilt < -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2;
            # when we jump back up it doesn't end up skipping time

    # Based on current tilt, modify the image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft= (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # This mask is used to compare the octopus and obstacle for collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Obstacle:
    """
       This class provides the obstacles that the octopus has to traverse.
       The obstacle would appear from both the top and bottom in turn helping to
       move where the gap appears. The height is randomly generated.
    """

    #GAP = 200
    GAP = 300
    VEL = 5

    # only x because the appearance of obstacle will be random on the screen
    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.OBSTACLE_TOP = pygame.transform.flip(OBSTACLE_IMG, False, True)
        self.OBSTACLE_BOTTOM = OBSTACLE_IMG
        # Flipping is required when the obstacle has to be upside down

        self.passed = False # for collision analysis and the AI later
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.OBSTACLE_TOP.get_height()
        # When the obstacle is at the top, it is upside down. So its top is somewher
        # in the middle of the image. So we need to subtract the height to actually
        # find its coordinates
        #self.bottom = self.height + self.GAP
        self.bottom = self.height + self.GAP
    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.OBSTACLE_TOP, (self.x ,self.top))
        win.blit(self.OBSTACLE_BOTTOM, (self.x, self.bottom))

# draw a box around each octopus.
# going to use masks - it can actually check if the pixels inside the boxes are touching.

    def collide(self, octopus):
        octopus_mask = octopus.get_mask()
        top_mask = pygame.mask.from_surface(self.OBSTACLE_TOP)
        bottom_mask = pygame.mask.from_surface(self.OBSTACLE_BOTTOM)

        # To calculate offset
        top_offset = (self.x - octopus.x, self.top - round(octopus.y))
        bottom_offset = (self.x - octopus.x, self.bottom - round(octopus.y))

        b_point = octopus_mask.overlap(bottom_mask, bottom_offset)
        #b_point will be none if there is no collision
        t_point = octopus_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    """
    This class provides a sort of based that indicates the movement of the octopus.
    In a future version, I would like to add more details to this base

    The base is repeated through two back-to-back copies that replace one after the other
    so as to give an illusion that this is a never ending sea floor. This is implemented using the
    move() method

    """
    VEL = 5 # should be same as obstacle
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    HEIGHT = BASE_IMG.get_height()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH # x1, x2 are two versions of the base image and move one behind the other and cycle

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))




def draw_window(win, octopi, obstacles, base, score, gen):
    """
    This function would use used to draw the game window with all the components.
    """

    if gen == 0: # gen is used to display the generation (0th generation would be misleading)
        gen = 1
    win.blit(BG_IMG, (0,0))

    base.draw(win)

    for obstacle in obstacles:
        obstacle.draw(win)

    for octopus in octopi:
        octopus.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    pygame.display.update()
