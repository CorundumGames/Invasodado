import math
import random

import pygame

import blockgrid
import config
import color
import ingame
import gameobject

STATES    = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'FALLING', 'IMPACT', 'DYING')
FRAME     = pygame.Rect(0, 32, 16, 16)
GRAVITY   = .5
MAX_SPEED = 12.0

bump = pygame.mixer.Sound("./bump.wav")


class Block(gameobject.GameObject):
    '''Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    def __init__(self, pos):
        gameobject.GameObject.__init__(self)
        self.actions = {
                        STATES.IDLE     : None          ,
                        STATES.APPEARING: NotImplemented,
                        STATES.ACTIVE   : self.wait     ,
                        STATES.FALLING  : self.fall     ,
                        STATES.IMPACT   : self.stop     ,
                        STATES.DYING    : self.vanish
                        }
        
        self.acceleration[1] = GRAVITY
        self.block_below     = None
        self.color           = random.choice(color.Colors.LIST)
        self.image           = config.SPRITES.subsurface(FRAME).copy()  #@UndefinedVariable
        self.rect            = pygame.Rect(math.floor(pos[0]/16.0)*16,
                                           math.floor(pos[1]/16.0)*16, 16, 16)
        self.state           = STATES.FALLING
        
        self.gridcell        = (self.rect.left/self.rect.width,
                                self.rect.top/self.rect.height)
        self.position        = list(self.rect.topleft)
        
        
        self.add(ingame.BLOCKS)
        
        #Blend the sprite with the assigned color.
        self.image = color.blend_color(self.image, self.color)
        
    def __str__(self):
        return "Block of color " + str(self.color) + " at grid cell" + str(self.gridcell)
        
    def on_collide(self, other):
        if isinstance(other, Block) and self.state == STATES.FALLING\
        and other.gridcell == (self.gridcell[0], self.gridcell[1]+1):
        #If we hit a block, we're falling, and the block we hit is a cell below us...
            self.block_below = other
            self.rect.bottom = other.rect.top
            self.state       = STATES.IMPACT       
            
    def wait(self):
        '''Constantly checks to see if this block can fall.  Gets it moving
        if so.
        '''
        if isinstance(self.block_below, Block):
        #If there exists a block underneath us and we're not at the bottom...
            if self.rect.bottom < blockgrid.RECT.bottom\
            and self.rect.bottom != self.block_below.rect.top:
            #If we're not at the bottom and there's no block directly below...
                self.acceleration[1] = GRAVITY
                if self in blockgrid.blockstocheck: blockgrid.blockstocheck.remove(self)
                self.state           = STATES.FALLING
        
    def fall(self):
        self.velocity[1]  = min(MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        self.rect.topleft = map(round, self.position)
        self.gridcell     = (self.rect.left/self.rect.width,
                             self.rect.top/self.rect.height)
        
        if self.rect.bottom > blockgrid.RECT.bottom:  #@UndefinedVariable
        #If we've hit the grid's bottom...
            self.rect.bottom = blockgrid.RECT.bottom
            self.state       = STATES.IMPACT
            
    def stop(self):
        #Stop all motion
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.gridcell        = (self.rect.left/self.rect.width,
                                self.rect.top/self.rect.height)
        blockgrid.blockstocheck.add(self)  #Might remove later?
        bump.play()
        
        self.state           = STATES.ACTIVE
        
    def vanish(self):
        self.kill()
        if self in blockgrid.blockstocheck: blockgrid.blockstocheck.remove(self)
        self.block_below                                     = None
        self.position                                        = [-300.0, -300.0]
        self.rect.topleft                                    = self.position
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        self.gridcell                                        = None
        self.state                                           = STATES.IDLE
           
    def snap(self):
        self.rect.topleft = (math.floor(self.position[0]/16)*16,
                             math.floor(self.position[1]/16)*16)