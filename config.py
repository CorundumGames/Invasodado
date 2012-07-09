import pygame
import settings
import enum

pygame.display.init()

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution)

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

#The main spritesheet for this game.
SPRITES = pygame.image.load("./gfx/sprites.png").convert()

COLOR_KEY = SPRITES.get_at((0, 0))

COLORS = {
    'RED'   : pygame.Color(255,   0,   0),
    'BLUE'  : pygame.Color(  0, 255,   0),
    'GREEN' : pygame.Color(  0,   0, 255),
    'YELLOW': pygame.Color(255, 255,   0),
    'PURPLE': pygame.Color(255,   0, 255),
    'WHITE' : pygame.Color(255, 255, 255),
    'BLACK' : pygame.Color(  0,   0,   0)
    }