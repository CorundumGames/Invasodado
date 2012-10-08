import pygame.display
import pygame.image

import settings

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution)

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

SCALE_FACTOR = 2

#The main spritesheet for this game.
SPRITES = pygame.image.load("./gfx/sprites.png").convert()
SPRITES = pygame.transform.scale(SPRITES, (SPRITES.get_width()*SCALE_FACTOR, SPRITES.get_height()*SCALE_FACTOR))

#The background
BG = pygame.image.load("./gfx/bg.png").convert()

class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))