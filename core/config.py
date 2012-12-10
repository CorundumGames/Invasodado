import pygame.display
import pygame.image

import settings

screen = pygame.display.set_mode(settings.resolution, pygame.DOUBLEBUF)
#The window we blit graphics onto.

SCREEN_DIMS = tuple(pygame.display.list_modes())
#A tuple of all available screen resolutions.

NUM_COLORS = 5
#How many colors we'll use for the blocks

FLAGS = pygame.HWSURFACE | pygame.HWACCEL | pygame.ASYNCBLIT | pygame.RLEACCEL
#The flags used to create all Surfaces; these are best for performance.

DEPTH = screen.get_bitsize()
#The color depth used, in bits

SCREEN_WIDTH  = screen.get_width()  #640 20 cells 32
SCREEN_HEIGHT = screen.get_height() #480 15 cells 32
#Screen width and height, in pixels

SPRITES = pygame.image.load("./gfx/sprites.png").convert(DEPTH, FLAGS)
#The main spritesheet for this game.

BG = pygame.image.load("./gfx/bg.png").convert(DEPTH, FLAGS)
#The background

FONT = pygame.font.Font("./gfx/font.ttf", 18)
#The main typeface we will use; we might use more.

pause = False
#True if the game is paused

limit_frame = True
#True if we're restricting framerate to 60FPS

debug = False
#True if we're in debug mode

class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))


def toggle_fullscreen():
#Toggles fullscreen.
    settings.fullscreen = not settings.fullscreen
    screen = pygame.display.set_mode(settings.resolution, (pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) * settings.fullscreen )

def toggle_pause():
#Handles pausing of the game...
    global pause
    pause = not pause
    
    while pause:
    #While the game is paused...
        for event in pygame.event.get():
        #For all received events...
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            #If the P key is pressed...
                pause = not pause
                break
def toggle_frame_limit():
    global limit_frame
    limit_frame = not limit_frame
    
def toggle_debug():
    global debug
    debug = not debug