import pygame
import settings

pygame.display.init()

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())
SCREEN_DIMS.reverse()

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution)