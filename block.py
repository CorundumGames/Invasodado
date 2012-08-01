import math
import random

import pygame

import config
import color
import ingame
import gameobject

STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'FALLING', 'DYING')
FRAME  = pygame.Rect(0, 32, 16, 16)

class Block(gameobject.GameObject):
    def __init__(self, pos):
        gameobject.GameObject.__init__(self)
        self.actions = {
                        STATES.IDLE     : None,
                        STATES.APPEARING: NotImplemented,
                        STATES.ACTIVE   : NotImplemented,
                        STATES.FALLING  : NotImplemented,
                        STATES.DYING    : NotImplemented
                        }
        self.image = config.SPRITES.subsurface(FRAME).copy()  #@UndefinedVariable
        self.rect = pygame.Rect(math.floor(pos[0]/16.0)*16, math.floor(pos[1]/16.0)*16, 16, 16)
        self.state = STATES.ACTIVE
        
        self.add(ingame.BLOCKS)
        self.image = color.blend_color(self.image, random.choice(color.Colors.LIST))