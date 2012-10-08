'''Invasodado alpha 1

Invasodado is a mix between Space Invaders and Columns.

Copyright 2012 Corundum Games
'''

import pygame.display
import pygame.event
import pygame.mixer

pygame.mixer.init()
pygame.display.init()

from core import config
from core import gsm

while True:
    gsm.update()
    
    if pygame.event.peek(pygame.QUIT):
        break