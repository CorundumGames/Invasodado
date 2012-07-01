import config
import pygame
import gsm

while True:
    gsm.update()
    
    if pygame.event.peek(pygame.QUIT):
        quit()
    
    