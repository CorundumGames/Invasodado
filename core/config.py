'''
Contains a whole bunch of game-specific miscellaneous constants, functions,
utilities, etc.  It's a Python convention to call this sort of file config.py.
'''

from functools import lru_cache
from os.path import join
from sys     import argv

from pygame.display import set_caption
import pygame.image
from pygame.constants import *

from core import settings

### Globals ####################################################################

#The window we blit graphics onto.

_current_difficulty = 1

_difficulties = ["Easy", "Normal", "Hard"]

_limit_frame = True
#True if we're restricting framerate to 60FPS

_music_playing = None

_pause = False
#True if the game is paused

_sounds = []

fps_timer = pygame.time.Clock()

screen = pygame.display.set_mode(settings.resolution, DOUBLEBUF)

tracking = __debug__ and 'track' in argv
#True if we're outputting graphs of the player's statistics

################################################################################



### Functions ##################################################################
@lru_cache(maxsize=16)
def difficulty_string():
    return _difficulties[_current_difficulty]

def get_sprite(frame):
    return SPRITES.subsurface(frame).copy()

def load_image(name):
    return pygame.image.load(join('gfx', name)).convert(DEPTH, FLAGS)

def load_sound(name):
    sound = pygame.mixer.Sound(join('sfx', name))
    _sounds.append(sound)
    return sound

@lru_cache(maxsize=4)
def on_off(condition):
    '''
    Primarily for the Settings menu.
    '''
    return "On" if condition else "Off"

@lru_cache(maxsize=16)
def percent_str(var):
    return "%d%%" % (var * 100)

def play_music(name):
    '''
    Plays a music file
    '''
    global _music_playing
    if name != _music_playing:
    #If we want to play a song that isn't already playing...
        _music_playing = name
        pygame.mixer.music.load(join('sfx', name))
        pygame.mixer.music.play(-1)
        
def set_volume():
    for i in _sounds:
        i.set_volume(settings.sound_volume)

def show_fps():
    set_caption("FPS: %3g" % round(fps_timer.get_fps(), 3))
    
def toggle_color_blind_mode():
    '''
    Toggles color-blind mode.
    '''
    settings.color_blind = not settings.color_blind
    
def toggle_difficulty(toggle):
    '''
    Toggles difficulty
    '''
    #TODO: Improve documentation
    global _current_difficulty
    _current_difficulty += toggle
    _current_difficulty %= len(_difficulties)
    
def toggle_frame_limit():
    '''
    Toggles the regulation of the frame rate.  If unregulated, the game runs as
    fast as the computer can process it.
    '''
    global _limit_frame
    _limit_frame = not _limit_frame

def toggle_fullscreen():
    '''
    Toggles full-screen on or off.
    
    @postcondition: If the game wasn't in full-screen before, it is now, or vice versa.
    '''
    global screen
    settings.fullscreen = not settings.fullscreen
    screen = pygame.display.set_mode(settings.resolution,
                                     (FULLSCREEN | HWSURFACE | DOUBLEBUF)
                                     * settings.fullscreen
                                    )

def toggle_pause():
    '''
    Pauses the game.
    '''

    global _pause
    _pause = not _pause
    pygame.mixer.pause()
    PAUSE.play()
    #TODO: Make the pausing user-friendly.  No game these days just freezes.
    pygame.mixer.music.pause()
    
    while _pause:
    #While the game is paused...
        for event in pygame.event.get():
        #For all received events...
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            #If the P key is pressed...
                _pause = not _pause
                PAUSE.play()
                pygame.mixer.unpause()
                pygame.mixer.music.unpause()
                break

################################################################################

### Constants ##################################################################
CURSOR_BEEP   = load_sound('cursor.wav')
CURSOR_SELECT = load_sound('select.wav')
DEPTH    = screen.get_bitsize()
ENCODING = 'utf-8'
FLAGS    = HWSURFACE | HWACCEL | ASYNCBLIT | RLEACCEL
#The flags used to create all Surfaces; these are best for performance.

NUM_COLORS = 5
#The color depth used, in bits
PAUSE = load_sound('pause.wav')
SCREEN_DIMS   = tuple(pygame.display.list_modes()) #Available screen resolutions
SCREEN_HEIGHT = screen.get_height() #480 15 cells 32
SCREEN_RECT   = pygame.Rect((0, 0), screen.get_size())
SCREEN_WIDTH  = screen.get_width()  #640 20 cells 32
#Screen width and height, in pixels
SPRITES = load_image('sprites.png')
EARTH   = load_image('earth.png')
BG      = load_image('bg.png')
FONT    = pygame.font.Font(join('gfx', 'font.ttf'), 18)
################################################################################

### Preparation ################################################################
for i in (EARTH, BG):
    i.set_colorkey(pygame.Color('#000000'))

BG.set_alpha(128)
EARTH = EARTH.subsurface(pygame.Rect(0, 0, EARTH.get_width(), EARTH.get_height()/2))

if not __debug__:
    del show_fps
    del tracking
################################################################################

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
