import Image
import pygame

import config

#The color that will be transparent.
COLOR_KEY = config.SPRITES.get_at((0, 0))  #@UndefinedVariable

#The desired color mode for our graphics.
COLOR_MODE = "RGBA"

class Colors:
    RED    = pygame.Color(255,   0,   0)
    GREEN  = pygame.Color(  0, 255,   0)
    BLUE   = pygame.Color(  0,   0, 255)
    YELLOW = pygame.Color(255, 255,   0)
    PURPLE = pygame.Color(153,   0, 153)
    
    LIST = [RED, BLUE, GREEN, YELLOW, PURPLE]

def blend_color(surface, color):
    '''Returns a new Surface blended with the given color.'''
    colorsurface = Image.new(COLOR_MODE, surface.get_size(), (color.r, color.g, color.b, color.a))
    temp = Image.fromstring(COLOR_MODE, surface.get_size(),
                            pygame.image.tostring(surface, COLOR_MODE))
    temp = Image.blend(temp, colorsurface, 0.5)
    
    return pygame.image.fromstring(temp.tostring(), surface.get_size(), COLOR_MODE)