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

pause = False

while True:
    if pygame.key.get_pressed()[pygame.K_F1]:
        settings.fullscreen = not settings.fullscreen
        config.screen = pygame.display.set_mode(settings.resolution, (pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) * settings.fullscreen )
    elif keys[pygame.K_ESCAPE]:
        break

    for event in pygame.event.get(pygame.KEYDOWN):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                print(pause)
                pause = not pause
        pygame.event.clear(pygame.KEYDOWN)
        
    if not pause:
        gsm.update()
        
    if pygame.event.peek(pygame.QUIT):
        break
    
if __name__ == '__main__':
    main()
