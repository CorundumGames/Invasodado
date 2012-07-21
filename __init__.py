import config
import pygame
import gsm

pygame.display.init()
pygame.display.get_surface().fill((0, 0, 0))

while True:
    gsm.update()
    
    if pygame.event.peek(pygame.QUIT):
        quit()