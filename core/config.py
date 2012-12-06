import pygame.display
import pygame.image

import settings

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution, pygame.DOUBLEBUF)

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

#How many colors we'll use
NUM_COLORS = 5

FLAGS = pygame.HWSURFACE | pygame.HWACCEL | pygame.ASYNCBLIT | pygame.RLEACCEL

DEPTH = screen.get_bitsize()

#Screen Width and Height
SCREEN_WIDTH  = screen.get_width()  #640 20 cells 32
SCREEN_HEIGHT = screen.get_height() #480 15 cells 32

#The main spritesheet for this game.
SPRITES = pygame.image.load("./gfx/sprites.png").convert(DEPTH, FLAGS)

#The background
BG = pygame.image.load("./gfx/bg.png").convert(DEPTH, FLAGS)


FONT = pygame.font.Font("./gfx/font.ttf", 18)

class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))