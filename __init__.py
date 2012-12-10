'''
Invasodado alpha 2

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
from game import mainmenu

def main():
    while True:
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            return
        
        gsm.update()
        
        if pygame.event.peek(pygame.QUIT):
            return
        
if __name__ == '__main__':
    main()
