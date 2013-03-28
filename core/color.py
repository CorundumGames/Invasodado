'''
This module just provides some useful tools for the various color-reliant
objects in Invasodado to use.  Nothing too special here.
'''
from random import uniform, choice

from pygame.constants import *
from pygame import Color, Rect

from core import config
from core import settings
from core.particles import ParticlePool

### Constants #################################################################

# Common colors we would refer to; not all of these are used by blocks!
RED    = Color('#FF3333')
GREEN  = Color('#4FFF55')
BLUE   = Color('#585EFF')
YELLOW = Color('#EBFF55')
PURPLE = Color('#FF55D5')
WHITE  = Color('#FFFFFF')
BLACK  = Color('#000000')
LIST   = (RED, BLUE, GREEN, YELLOW, PURPLE) # THESE are used by blocks.

# The color that will be transparent, taken from the bottom-left corner
COLOR_KEY = config.SPRITES.get_at((0, config.SPRITES.get_height() - 1))

#Holds the frames for the symbols
COLOR_BLIND_FRAMES  = tuple(Rect(32 * i, 32, 32, 32) for i in range(4,10))
#Holds the symbols.
COLOR_BLIND_SYMBOLS = {
                        id(RED)    : config.get_sprite(COLOR_BLIND_FRAMES[0]),
                        id(BLUE)   : config.get_sprite(COLOR_BLIND_FRAMES[1]),
                        id(GREEN)  : config.get_sprite(COLOR_BLIND_FRAMES[2]),
                        id(YELLOW) : config.get_sprite(COLOR_BLIND_FRAMES[3]),
                        id(PURPLE) : config.get_sprite(COLOR_BLIND_FRAMES[4]),
                        id(WHITE)  : config.get_sprite(COLOR_BLIND_FRAMES[5])
                       }
################################################################################

### Functions ##################################################################
def blend_color(surface, color):
    '''
    Returns a new Surface blended with the given color.
    
    @param surface: The graphic to be tinted
    @param color: The color to tint surface with
    '''
    surface.fill(color, special_flags=BLEND_RGBA_MULT)
    return surface

def get_colored_objects(frames, has_alpha=True, color_blind=False, pause_frame = False):
    '''
    @param frames: List of sprites we want to create colored versions of
    @param has_alpha: True if we want transparency

    @rtype: dict of {color: [frames_list]}
    '''
    colored = dict([
                    (id(c), [blend_color(config.get_sprite(f), c) for f in frames])
                    for c in LIST
                   ]
                  )
    if pause_frame:
        colored[id(WHITE)] = [blend_color(config.get_sprite(f), WHITE) for f in frames]

    if has_alpha:
    #If we want these frames to have transparency...
        for i in colored.values():
        #For all given frames...
            for j in i:
                j.set_colorkey(j.get_at([0, 0]), config.BLIT_FLAGS)
                
    if color_blind:
        for c in LIST:
            COLOR_BLIND_SYMBOLS[id(c)].set_colorkey(COLOR_KEY)
        for c in LIST:
            for i in colored[id(c)]:
                i.blit(COLOR_BLIND_SYMBOLS[id(c)].copy(), (0, 0))
    return colored

def _rand_color_appear(self):
    self.acceleration[1] = 0.5
    self.velocity        = [uniform(-5, 5), uniform(-1, -3)]
    self.image           = choice(list(_parts.values()))[0]
################################################################################

### Globals ####################################################################
_parts                 = get_colored_objects([Rect(4, 170, 4, 4)], False)
color_particles        = dict([(id(c), ParticlePool(_parts[id(c)][0])) for c in LIST])
random_color_particles = ParticlePool(_parts[id(RED)][0], appear_func=_rand_color_appear)
################################################################################