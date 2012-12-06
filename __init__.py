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
from game import mainmenu


gsm.current_state = mainmenu.MainMenu()

def main():
    while True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_F1]:
            settings.fullscreen = not settings.fullscreen
            config.screen = pygame.display.set_mode(settings.resolution, (pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) * settings.fullscreen )
        elif keys[pygame.K_ESCAPE]:
            break
    
        gsm.update()
    
        if pygame.event.peek(pygame.QUIT):
            break
        
if __name__ == '__main__':
    main()