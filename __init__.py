'''Invasodado alpha 1

Invasodado is a mix between Space Invaders and Columns.

Copyright 2012 Corundum Games
'''

import pygame

pygame.mixer.init()

from core import config
from core import gsm


pygame.display.init()

pygame.display.get_surface().fill((0, 0, 0))

while True:
    gsm.update()
    
    if pygame.event.peek(pygame.QUIT):
        break