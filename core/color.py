import Image
import pygame.color
import pygame.image

import config

COLOR_KEY  = config.SPRITES.get_at((0, 0))
#The color that will be transparent.

COLOR_MODE = "RGBA"
#The desired color mode for our graphics.

#Common colors we would refer to; not all of these are used by blocks!  #######
RED    = pygame.Color(255,   0,   0)
GREEN  = pygame.Color(  0, 255,   0)
BLUE   = pygame.Color(  0,   0, 255)
YELLOW = pygame.Color(255, 255,   0)
PURPLE = pygame.Color(153,   0, 153)
WHITE  = pygame.Color(255, 255, 255)
###############################################################################
    
LIST = [RED, BLUE, GREEN, YELLOW, PURPLE]
#THESE are all used by blocks.

def blend_color(surface, color):
    '''
    Returns a new Surface blended with the given color.
    '''
    size         = surface.get_size()
    colorsurface = Image.new(COLOR_MODE, size, tuple(color))
    temp         = Image.fromstring(COLOR_MODE,
                                    size,
                                    pygame.image.tostring(surface, COLOR_MODE))
    temp         = Image.blend(temp, colorsurface, 0.5)
    
    return pygame.image.fromstring(temp.tostring(), size, COLOR_MODE).convert(config.DEPTH, config.FLAGS)