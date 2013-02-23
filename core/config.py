'''
Contains a whole bunch of game-specific miscellaneous constants, functions,
utilities, etc.  It's a Python convention to call this sort of file config.py.
'''

from os.path import join
import sys

import pygame.display
import pygame.image

from core import settings

screen = pygame.display.set_mode(settings.resolution, pygame.DOUBLEBUF)
#The window we blit graphics onto.

SCREEN_DIMS = tuple(pygame.display.list_modes())
#A tuple of all available screen resolutions.

SCREEN_RECT = pygame.Rect((0, 0), screen.get_size())

FLAGS = pygame.HWSURFACE | pygame.HWACCEL | pygame.ASYNCBLIT | pygame.RLEACCEL
#The flags used to create all Surfaces; these are best for performance.

NUM_COLORS = 5

ENCODING = 'utf-8'

DEPTH = screen.get_bitsize()
#The color depth used, in bits

SCREEN_WIDTH  = screen.get_width()  #640 20 cells 32
SCREEN_HEIGHT = screen.get_height() #480 15 cells 32
#Screen width and height, in pixels

SPRITES = pygame.image.load(join('gfx', 'sprites.png')).convert(DEPTH, FLAGS)
#The main spritesheet for this game.

EARTH   = pygame.image.load(join('gfx', 'earth.png'  )).convert(DEPTH, FLAGS)
EARTH.set_colorkey(pygame.Color('#000000'))

BG      = pygame.image.load(join('gfx', 'bg.png'     )).convert(DEPTH, FLAGS)
BG.set_colorkey(pygame.Color('#000000'))
BG.set_alpha(128)
#The background

FONT    = pygame.font.Font(join('gfx', 'font.ttf'), 18)
#The main typeface we will use; we might use more.

_pause = False
#True if the game is paused

_limit_frame = True
#True if we're restricting framerate to 60FPS

tracking = __debug__ and 'track' in sys.argv
#True if we're outputting graphs of the player's statistics

class Enum:
    '''
    A simple class I copied and pasted from StackOverflow that lets us use the
    enum-like syntax I miss so much.  Associates integers to Python variable
    names, which are generated dynamically.
    '''
    def __init__(self, *keys):
        '''
        @param keys: List of enum entries, given as a list of strings
        '''
        self.__dict__.update(zip(keys, range(len(keys))))


def toggle_fullscreen():
    '''
    Toggles full-screen on or off.
    
    @postcondition: If the game wasn't in full-screen before, it is now, or vice versa.
    '''
    global screen
    settings.fullscreen = not settings.fullscreen
    screen = pygame.display.set_mode(settings.resolution,
                                     (
                                      pygame.FULLSCREEN |
                                      pygame.HWSURFACE  |
                                      pygame.DOUBLEBUF
                                     ) * settings.fullscreen
                                    )

def toggle_pause():
    '''
    Pauses the game.
    '''
    global _pause
    _pause = not _pause

    #TODO: Make the pausing user-friendly.  No game these days just freezes.
    while _pause:
    #While the game is paused...
        for event in pygame.event.get():
        #For all received events...
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            #If the P key is pressed...
                _pause = not _pause
                break

def toggle_frame_limit():
    '''
    Toggles the regulation of the frame rate.  If unregulated, the game runs as
    fast as the computer can process it.
    '''
    global _limit_frame
    _limit_frame = not _limit_frame
    
def toggle_color_blind_mode():
    settings.color_blind = not settings.color_blind

def on_off(condition):
    return "On" if condition else "Off"