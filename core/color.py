import pygame.color
import pygame.image

import config

COLOR_KEY  = config.SPRITES.get_at((0, config.SPRITES.get_height()-1))
#The color that will be transparent.

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

def blend_color(surface, color):
    '''
    Returns a new Surface blended with the given color.
    '''
    surface.fill(color, special_flags = pygame.BLEND_RGBA_MULT)
    return surface
