import pygame

import settings

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution)

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

#The main spritesheet for this game.
SPRITES = pygame.image.load("./gfx/sprites.png").convert()

BG = pygame.image.load("./gfx/bg.png").convert()

class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))