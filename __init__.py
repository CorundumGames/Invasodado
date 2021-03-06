'''
Invasodado beta 3

Invasodado is a mix between Space Invaders and Columns.

Copyright 2012-2013 Corundum Games
'''

import atexit
from os.path import join
import sys
import warnings

warnings.simplefilter('ignore')

import pygame.display
import pygame.event
import pygame.mixer

pygame.mixer.init(44100)
pygame.font.init()
pygame.display.init()

from core import config
from core import settings
import core.gsm as gsm

@atexit.register
def close():
    pygame.display.quit()
    pygame.mixer.quit()
    pygame.font.quit()

def main():
    '''
    Meant to be executed only once.  main() exists to facilitate profiling, as
    cProfile wants a function, not a module.
    '''
    settings.load_settings(join(config.DATA_STORE, 'settings.wtf'))
    pygame.display.set_caption("Invasodado")
    #Set the sounds now that we loaded the correct volumes
    config.set_volume()
    config.init_music_volume()
    if not sys.stdout:
        class Dummy:
            def write(self, *args, **kwargs):
                pass
                
        sys.stdout = Dummy()
        sys.stdin = sys.stdout
        sys.stderr = sys.stdout
    
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
    data.sort_stats('calls')
    data.print_stats()

if __name__ == '__main__':
#If this script is being executed directly...
    if 'profile' in sys.argv:
    #If we're profiling the game...
        profile()
    else:
        main()
