import pygame.display
import pygame.image

import settings

#The window we blit graphics onto.
screen = pygame.display.set_mode(settings.resolution, pygame.DOUBLEBUF)

#A tuple of all available screen resolutions.
SCREEN_DIMS = tuple(pygame.display.list_modes())

#How many colors we'll use
NUM_COLORS = 5

FLAGS = pygame.HWSURFACE | pygame.HWACCEL | pygame.ASYNCBLIT | pygame.RLEACCEL
#The flags used to create all Surfaces; these are best for performance.

DEPTH = screen.get_bitsize()

#Screen Width and Height
SCREEN_WIDTH  = screen.get_width()  #640 20 cells 32
SCREEN_HEIGHT = screen.get_height() #480 15 cells 32

#The main spritesheet for this game.
SPRITES = pygame.image.load("./gfx/sprites.png").convert(DEPTH, FLAGS)

#The background
BG = pygame.image.load("./gfx/bg.png").convert(DEPTH, FLAGS)


FONT = pygame.font.Font("./gfx/font.ttf", 18)
#The main typeface we will use; we might use more.

pause = False
#True if the game is paused

class Enum(object):
    def __init__(self, *keys):
        self.__dict__.update(zip(keys, range(len(keys))))


def fullScreen():
#Toggles fullscreen.
    settings.fullscreen = not settings.fullscreen
    screen = pygame.display.set_mode(settings.resolution, (pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) * settings.fullscreen )

def togglePause():
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