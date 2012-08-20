import math
import random

import pygame

import config
import color
import ingame
import gameobject

STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'FALLING', 'DYING')
FRAME  = pygame.Rect(0, 32, 16, 16)
GRAVITY = .5

class Block(gameobject.GameObject):
    def __init__(self, pos):
        gameobject.GameObject.__init__(self)
        self.actions = {
                        STATES.IDLE     : None,
                        STATES.APPEARING: NotImplemented,
                        STATES.ACTIVE   : NotImplemented,
                        STATES.FALLING  : self.fall     ,
                        STATES.DYING    : NotImplemented
                        }
        
        self.acceleration[1] = GRAVITY
        self.image = config.SPRITES.subsurface(FRAME).copy()  #@UndefinedVariable
        self.rect = pygame.Rect(math.floor(pos[0]/16.0)*16, math.floor(pos[1]/16.0)*16, 16, 16)
        self.position = list(self.rect.topleft)
        self.state = STATES.FALLING
        
        self.add(ingame.BLOCKS)
        self.image = color.blend_color(self.image, random.choice(color.Colors.LIST))
        
    def on_collide(self, other):
        if isinstance(other, Block) and self.state == STATES.FALLING and other.state == STATES.ACTIVE:
            self.acceleration[1] = 0
            self.velocity[1] = 0
            self.rect.bottom = other.rect.top
            
            self.state = STATES.ACTIVE
        
    def fall(self):
        self.velocity[1] += self.acceleration[1]
        self.position[1] += self.velocity[1]
        self.rect.topleft = map(round, self.position)
        
        if self.rect.bottom >= config.screen.get_height() * .9:
            self.acceleration[1] = 0
            self.velocity[1] = 0
            self.snap()
            self.state = STATES.ACTIVE
            
    def snap(self):
        self.rect.topleft = (math.floor(self.position[0]/16)*16, math.floor(self.position[1]/16)*16)