'''
This module just provides some useful tools for the various color-reliant
objects in Invasodado to use.  Nothing too special here.
'''
from random import uniform, choice

from pygame.constants import *
from pygame           import Color, Rect

from core           import config
from core.particles import ParticlePool

### Constants #################################################################
'''
@var RED, GREEN, BLUE, YELLOW, PURPLE, WHITE, BLACK: Common game colors.
     They are not necessarily "pure" (i.e. BLUE isn't #0000FF).
@var LIST: Colors that in-game objects are allowed to be.
@var COLOR_KEY: The transparent color on the main spritesheet, defaults to
     whatever's in the bottom-left corner.
@var COLOR_BLIND_FRAMES: The shapes that are placed over game objects in colorblind mode.
@var COLOR_BLIND_SYMBOLS: Mapping of LIST plus WHITE to COLOR_BLIND_FRAMES
'''

RED    = Color('#FF3333')
GREEN  = Color('#4FFF55')
BLUE   = Color('#585EFF')
YELLOW = Color('#EBFF55')
PURPLE = Color('#FF55D5')
WHITE  = Color('#FFFFFF')
BLACK  = Color('#000000')

COLOR_BLIND_FRAMES  = tuple(Rect(32 * i, 32, 32, 32) for i in range(4,10))
COLOR_BLIND_SYMBOLS = {
                        id(RED)    : config.get_sprite(COLOR_BLIND_FRAMES[0]),
                        id(BLUE)   : config.get_sprite(COLOR_BLIND_FRAMES[1]),
                        id(GREEN)  : config.get_sprite(COLOR_BLIND_FRAMES[2]),
                        id(YELLOW) : config.get_sprite(COLOR_BLIND_FRAMES[3]),
                        id(PURPLE) : config.get_sprite(COLOR_BLIND_FRAMES[4]),
                        id(WHITE)  : config.get_sprite(COLOR_BLIND_FRAMES[5])
                       }
COLOR_KEY           = config.SPRITES.get_at((0, config.SPRITES.get_height() - 1))
LIST                = (RED, BLUE, GREEN, YELLOW, PURPLE)
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

def get_colored_objects(frames, has_alpha=True, color_blind=False, pause_frame=True):
    '''
    @param frames: List of sprites we want to create colored versions of
    @param has_alpha: True if we want transparency
    @param color_blind: True if we want colorblind-friendly frames
    @param pause_frame: True if we want these to be all white

    @rtype: dict of {color: [frames_list]}
    '''

    colored = {id(c):tuple(blend_color(config.get_sprite(f), c) for f in frames) for c in LIST}
    if pause_frame:
    #If we're pausing the game...                       
        colored[id(WHITE)] = tuple(blend_color(config.get_sprite(f), WHITE) for f in frames)

    if has_alpha:
    #If we want these frames to have transparency...
        for i in colored.values():
        #For all frame colors...
            for j in i:
            #For each frame...             
                j.set_colorkey(j.get_at((0, 0)), config.BLIT_FLAGS)
                
    if color_blind:
    #If we want a colorblind-friendly version of the sprite...                   
        for c in LIST:
        #For each possible game object color...                        
            COLOR_BLIND_SYMBOLS[id(c)].set_colorkey(COLOR_KEY)                   
            for i in colored[id(c)]:
            #For each colored frame of this particular color...                        
                i.blit(COLOR_BLIND_SYMBOLS[id(c)], (0, 0))
    
    return colored

def _rand_color_appear(self):
    '''
    A function assigned to particles that appear with a random color.
    
    @param self: The Particle object that has this function
    '''
    self.acceleration[1] = 0.5
    self.velocity        = [uniform(-5, 5), uniform(-1, -3)]
    self.image           = choice(list(_parts.values()))[0]

################################################################################

### Globals ####################################################################
'''
@var _parts: Images of colored Particles
@var color_particles: Mapping of colors to ParticlePools holding Particles of this color
@var random_color_particles: ParticlePool of randomly-colored Particles
'''
_parts                 = get_colored_objects((Rect(4, 170, 4, 4),), False)
color_particles        = {id(c):ParticlePool(_parts[id(c)][0]) for c in LIST}
random_color_particles = ParticlePool(_parts[id(RED)][0], appear_func=_rand_color_appear)
################################################################################
