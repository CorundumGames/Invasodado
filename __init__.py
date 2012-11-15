'''Invasodado alpha 1

Invasodado is a mix between Space Invaders and Columns.

Copyright 2012 Corundum Games
'''

import pygame.display
import pygame.event
import pygame.mixer

pygame.mixer.init()
pygame.display.init()
pygame.font.init()

from core import config
from core import gsm
from core import settings

while True:
    if pygame.key.get_pressed()[pygame.K_F1]:
        settings.fullscreen = not settings.fullscreen
        config.screen = pygame.display.set_mode(settings.resolution, pygame.FULLSCREEN * settings.fullscreen)
            
    
    gsm.update()
    
    if pygame.event.peek(pygame.QUIT):
        break