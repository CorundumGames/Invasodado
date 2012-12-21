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
    #Until the game is closed...
        gsm.update()
        
        if pygame.event.peek(pygame.QUIT):
        #If we've received a request to quit (either by the user or the OS)...
            return
        
if __name__ == '__main__':
    main()
