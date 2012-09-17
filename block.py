import math
import random

import pygame

import blockgrid
import config
import color
import ingame
import gameobject

STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'FALLING', 'IMPACT', 'DYING')
FRAME  = pygame.Rect(0, 32, 16, 16)
GRAVITY = .5

bump = pygame.mixer.Sound("./bump.wav")


class Block(gameobject.GameObject):
    def __init__(self, pos):
        gameobject.GameObject.__init__(self)
        self.actions = {
                        STATES.IDLE     : None,
                        STATES.APPEARING: NotImplemented,
                        STATES.ACTIVE   : self.wait,
                        STATES.FALLING  : self.fall     ,
                        STATES.IMPACT   : self.stop     ,
                        STATES.DYING    : self.vanish
                        }
        
        self.acceleration[1] = GRAVITY
        self.color = random.choice(color.Colors.LIST)
        self.image = config.SPRITES.subsurface(FRAME).copy()  #@UndefinedVariable
        self.rect = pygame.Rect(math.floor(pos[0]/16.0)*16, math.floor(pos[1]/16.0)*16, 16, 16)
        self.gridcell = (self.rect.left/self.rect.width, self.rect.top/self.rect.height)
        self.position = list(self.rect.topleft)
        self.state = STATES.FALLING
        
        self.add(ingame.BLOCKS)
        
        self.image = color.blend_color(self.image, self.color)
        
    def __str__(self):
        return "Block of color " + str(self.color) + " at grid position " + \
            str(self.gridcell)
        
    def on_collide(self, other):
        if isinstance(other, Block) and self.state == STATES.FALLING and other.gridcell == (self.gridcell[0], self.gridcell[1]+1):
            self.rect.bottom = other.rect.top
            self.snap()
            self.state = STATES.IMPACT       
            
    def wait(self):
        if self.rect.bottom > blockgrid.RECT.bottom and not blockgrid.blocks[self.gridcell[0]][self.gridcell[1]]:
            self.acceleration[1] = GRAVITY
            self.state           = STATES.FALLING
        
    def fall(self):
        self.velocity[1] += self.acceleration[1]
        self.position[1] += self.velocity[1]
        self.rect.topleft = map(round, self.position)
        self.gridcell = (self.rect.left/self.rect.width, self.rect.top/self.rect.height)
        
        if self.rect.bottom >= blockgrid.RECT.bottom or blockgrid.blocks[self.gridcell[0]][self.gridcell[1]]:  #@UndefinedVariable
            self.snap()
            self.state = STATES.IMPACT
            
    def stop(self):
        self.acceleration[1] = 0
        self.velocity[1]     = 0
        self.gridcell        = (self.rect.left/self.rect.width, self.rect.top/self.rect.height)
        bump.play()
        self.state           = STATES.ACTIVE
        
    def vanish(self):
        self.kill()
        self.position = [-300, -300]
        self.rect.topleft = self.position
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = False
        self.gridcell = None
        self.state = STATES.IDLE
           
    def snap(self):
        self.rect.topleft = (math.floor(self.position[0]/16)*16, math.floor(self.position[1]/16)*16)