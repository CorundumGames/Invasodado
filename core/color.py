'''
This module just provides some useful tools for the various color-reliant
objects in Invasodado to use.  Nothing too special here.
'''

import pygame

from core import config
from core import settings

COLOR_KEY = config.SPRITES.get_at((0, config.SPRITES.get_height() - 1))
#The color that will be transparent, taken from the bottom-left corner

#Common colors we would refer to; not all of these are used by blocks!  #######
RED    = pygame.Color('#FF3333')
GREEN  = pygame.Color('#4FFF55')
BLUE   = pygame.Color('#585EFF')
YELLOW = pygame.Color('#EBFF55')
PURPLE = pygame.Color('#FF55D5')
WHITE  = pygame.Color('#FFFFFF')
###############################################################################

LIST = [RED, BLUE, GREEN, YELLOW, PURPLE]
#THESE are all used by blocks.

#Holds the frames for the symbols
COLOR_BLIND_FRAMES  = [pygame.Rect(32 * i, 32, 32, 32) for i in range(4,9)]
#Holds the symbols.
COLOR_BLIND_SYMBOLS = {
                        id(RED)    : config.SPRITES.subsurface(COLOR_BLIND_FRAMES[0]).copy(),
                        id(BLUE)   : config.SPRITES.subsurface(COLOR_BLIND_FRAMES[1]).copy(),
                        id(GREEN)  : config.SPRITES.subsurface(COLOR_BLIND_FRAMES[2]).copy(),
                        id(YELLOW) : config.SPRITES.subsurface(COLOR_BLIND_FRAMES[3]).copy(),
                        id(PURPLE) : config.SPRITES.subsurface(COLOR_BLIND_FRAMES[4]).copy()
                       }

def blend_color(surface, color):
    '''
    Returns a new Surface blended with the given color.
    
    @param surface: The graphic to be tinted
    @param color: The color to tint surface with
    '''
    surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return surface

def get_colored_objects(frames, has_alpha=True):
    '''
    @param frames: List of sprites we want to create colored versions of
    @param has_alpha: True if we want transparency

    @rtype: dict of {color: [frames_list]}
    '''
    colored = dict([
                    (
                     id(c),
                     [
                      blend_color(config.SPRITES.subsurface(f).copy(), c)
                      for f in frames
                     ]
                    )
                    for c in LIST
                   ]
                  )

    if has_alpha:
    #If we want these frames to have transparency...
        for i in colored.values():
        #For all given frames...
            for j in i:
                j.set_colorkey(j.get_at([0, 0]), config.FLAGS)
                
    if settings.color_blind:
        for c in LIST:
            COLOR_BLIND_SYMBOLS[id(c)].set_colorkey(COLOR_KEY)
        for c in LIST:
            for i in colored[id(c)]:
                i.blit(COLOR_BLIND_SYMBOLS[id(c)].copy(),(2,2))
    return colored