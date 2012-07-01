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

