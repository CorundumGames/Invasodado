'''
Contains a whole bunch of game-specific miscellaneous constants, functions,
utilities, etc.  It's a Python convention to call this sort of file config.py.
'''
from time      import strftime
from functools import lru_cache
from os        import environ
from os.path   import join
import sys

import pygame.image
from pygame.display   import set_caption
from pygame.constants import *
from pygame import Color
from pygame import Rect

from core import settings

### Globals ####################################################################

#The window we blit graphics onto.

_limit_frame = True
#True if we're restricting framerate to 60FPS

_music_playing = None

_pause = False
#True if the game is paused

_sounds = []

_sound_looping = None

fps_timer = pygame.time.Clock()

screen = pygame.display.set_mode(settings.SETTINGS['resolution'], DOUBLEBUF)

tracking = __debug__ and 'track' in sys.argv
#True if we're outputting graphs of the player's statistics

################################################################################



### Functions ##################################################################
def get_sprite(frame):
    return SPRITES.subsurface(frame).copy()

def load_image(name):
    a = pygame.image.load(join('gfx', name)).convert(DEPTH, BLIT_FLAGS)
    a.set_alpha(None)
    return a

def load_sound(name):
    sound = pygame.mixer.Sound(join('sfx', name))
    _sounds.append(sound)
    return sound

@lru_cache(maxsize=None)
def load_text(name, lang):
    with open(join('text', '%s-%s.wtf' % (name, lang)), encoding='utf-8') as text_file:
        return tuple(line.strip("\n") for line in text_file)
    
def loop_sound(sound):
    global _sound_looping
    if sound is None:
        if _sound_looping is not None:
            _sound_looping.stop()
        _sound_looping = None
    elif sound != _sound_looping:
        _sound_looping = sound
        _sound_looping.play(-1)

def on_off(condition):
    '''
    Primarily for the Settings menu.
    '''
    return ON_OFF[settings.get_language_code()][condition]

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
        i.set_volume(settings.SETTINGS['sound_volume'])
        
def init_music_volume():
    pygame.mixer.music.set_volume(settings.SETTINGS['music_volume'])

def show_fps():
    '''
    Displays the game's framerate on the window caption.  Meant to be called
    in Debug mode with assert statements so that this is effortlessly stripped
    out in Release mode.
    
    @invariant: MUST return an object that evaluates to False.
    '''
    set_caption("FPS: %3g" % round(fps_timer.get_fps(), 3))
    
def take_screenshot():
    pygame.image.save(pygame.display.get_surface(),
                      join(DATA_STORE, 'invasodado-%s.png' % strftime('%a-%b-%d-%Y_%H-%M-%S')))
    
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
    settings.SETTINGS['fullscreen'] = not settings.SETTINGS['fullscreen']
    screen = pygame.display.set_mode(settings.SETTINGS['resolution'], FULL_FLAGS * settings.SETTINGS['fullscreen'])

def toggle_pause():
    '''
    Pauses the game.
    '''

    global _pause
    _pause = not _pause
    pygame.mixer.pause()
    PAUSE.play()
    pygame.mixer.music.pause()
    
    while _pause:
    #While the game is paused...
        for event in pygame.event.get():
        #For all received events...
            if event.type == KEYDOWN and event.key == K_p:
            #If the P key is pressed...
                _pause = not _pause
                PAUSE.play()
                pygame.mixer.unpause()
                pygame.mixer.music.unpause()
                break
        fps_timer.tick(20)

################################################################################

### Constants ##################################################################
'''
@var APP_DATA_WIN: Environment variable holding the path of the Appdata folder
@var APP_DATA_LIN: Environment variable holding the path of the user's home directory
@var BLIT_FLAGS: The flags used by Pygame to render images a certain way
@var CURSOR_BEEP: The sound made when the player moves the menu cursor
@var CURSOR_SELECT: The sound made when the player selects a menu option
@var DATA_STORE: The directory we're storing Invasodado's save data
@var DEBUG: True if we're playing in debug mode
@var DEPTH: The color depth of the screen, in bits
@var EARTH: The image of the Earth in the background
@var ENCODING: The text encoding for Invasodado
@var EVENTS_OK: The events that this game will handle
@var FONT: The font used in this game
@var FULL_FLAGS: Flags used for rendering in full-screen mode
@var GRID_BG: The image for the grid that shows where blocks can fall
@var PAUSE: The sound played when the player pauses
@var SCREEN_DIMS: Tuple of all possible display resolutions
@var SCREEN_HEIGHT: Height of the screen, in pixels
@var SCREEN_RECT: pygame.Rect that represents screen's area
@var SCREEN_WIDTH: Width of the screen, in pixels
@var SPRITES: The spritesheet for the game
'''
            
APP_DATA_WIN = 'APPDATA'
APP_DATA_LIN = 'HOME'
BLIT_FLAGS    = HWSURFACE | HWACCEL | ASYNCBLIT | RLEACCEL
CURSOR_BEEP   = load_sound('cursor.wav')
CURSOR_SELECT = load_sound('select.wav')
DATA_STORE    = join(environ[APP_DATA_WIN if 'win' in sys.platform else APP_DATA_LIN], 'Invasodado')
DEBUG         =  __debug__ and not hasattr(sys, 'frozen') #cx_freeze adds 'frozen' to the sys module
DEPTH         = 8
EARTH         = load_image('earth.png')
ENCODING      = 'utf-8'
EVENTS_OK     = (KEYDOWN, MOUSEBUTTONDOWN, QUIT)
FONT          = pygame.font.Font(join('gfx', 'font.ttf'), 18)
FULL_FLAGS    = FULLSCREEN | HWSURFACE | DOUBLEBUF
GRID_BG       = load_image('bg.png')
ON_OFF        = {
                 'en' : ("Off", "On"),
                 'es' : ("No" , "Sí"),
                }
PAUSE         = load_sound('pause.wav')
SCREEN_DIMS   = tuple(pygame.display.list_modes())
SCREEN_HEIGHT = screen.get_height()
SCREEN_RECT   = Rect((0, 0), screen.get_size())
SCREEN_WIDTH  = screen.get_width()
SPRITES       = load_image('sprites.png')
################################################################################

### Preparation ################################################################
for i in (EARTH, GRID_BG):
    i.set_colorkey(Color('#000000'), BLIT_FLAGS)

GRID_BG.set_alpha(128)
EARTH = EARTH.subsurface(Rect(0, 0, EARTH.get_width(), EARTH.get_height() / 2))

if not DEBUG:
    del show_fps
    del tracking

pygame.event.set_allowed(None)
pygame.event.set_allowed(EVENTS_OK)
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
