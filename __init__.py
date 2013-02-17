'''
Invasodado alpha 2

Invasodado is a mix between Space Invaders and Columns.

Copyright 2012-2013 Corundum Games
'''
from sys import argv

import pygame.display
import pygame.event
import pygame.mixer

pygame.mixer.init()
pygame.display.init()
pygame.font.init()

from core import gsm

def main():
    '''
    Meant to be executed only once.  main() exists to facilitate profiling, as
    cProfile wants a function, not a module.
    '''
    pygame.display.set_caption("Invasodado")
    while True:
    #Until the game is closed...
        gsm.update()

        if pygame.event.peek(pygame.QUIT):
        #If we've received a request to quit (either by the user or the OS)...
            return
        
def profile():
    '''
    Call this function if we're profiling the game.
    '''
    import cProfile
    import pstats
        
    cProfile.run('main()', 'profile.out')
    data = pstats.Stats('profile.out')
    data.sort_stats('cumulative')
    data.print_stats()

if __name__ == '__main__':
    #If this script is being executed directly...
    if 'profile' in argv:
    #If we're not profiling the game...
        profile()
    else:
        main()
