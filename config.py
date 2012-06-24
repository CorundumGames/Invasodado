import pygame
import settings
import enum

pygame.display.init()

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

SPRITE_SHEET = pygame.image.load("./gfx/sprites.png").convert()

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution)