import sys
import random

import pygame.mixer

import core.color  as color
import core.config as config

import blockgrid
import gameobject
import ingame


FRAME = pygame.Rect(0, 64, 32, 32)


global blocks

bump = pygame.mixer.Sound("./sfx/bump.wav")

block_frames = dict([(id(c), color.blend_color(config.SPRITES.subsurface(FRAME).copy(), c)) for c in color.Colors.LIST])

class Block(gameobject.GameObject):
    '''Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    collisions = None
    GRAVITY    = .5
    MAX_SPEED  = 12.0
    STATES     = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')
    
    def __init__(self, pos, newcolor, specialblock = False):
        gameobject.GameObject.__init__(self)
        
        
        self.acceleration[1] = self.__class__.GRAVITY
        self.color           = newcolor
        self.image           = block_frames[id(self.color)]
        self.rect            = pygame.Rect(round(pos[0]/self.image.get_width())*self.image.get_width(),
                                           round(pos[1]/self.image.get_height())*self.image.get_height(),
                                           self.image.get_width(),
                                           self.image.get_height())
        
        
        self.gridcell        = [self.rect.centery/self.rect.height, #(row, column)
                                self.rect.centerx/self.rect.width]
        self.position        = list(self.rect.topleft)
        self.target          = blockgrid.DIMENSIONS[0] - 1
        
        self.state           = self.__class__.STATES.APPEARING
        self.special         = specialblock
        self.add(ingame.BLOCKS)
        
    def __str__(self):
        return "Block of color " + str(self.color) + " at grid cell " + str(self.gridcell) + " with target " + str(self.target)  
    
    def appear(self):
        self.state = self.__class__.STATES.START_FALLING
            
    def start_falling(self):
        global blocks
        bl = blockgrid.blocks
        blockgrid.blockstocheck.discard(self)
        for i in xrange(self.gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
                if isinstance(bl[i][self.gridcell[1]], Block):
                #If this grid cell is occupied...
                    self.target = i - 1
                    break
        
        if self.gridcell[0] > 0 and isinstance(bl[self.gridcell[0] - 1][self.gridcell[1]], Block):
        #If there is a block above us...
            for i in xrange(self.gridcell[0], 0, -1):
                if isinstance(bl[i][self.gridcell[1]], Block):
                    bl[i][self.gridcell[1]].state = self.__class__.STATES.START_FALLING
                else:
                    break
        
        self.state = self.__class__.STATES.FALLING
        
    def wait(self):
        '''Constantly checks to see if this block can fall.  Gets it moving
        if so.
        '''
        global blocks
        bl = blockgrid.blocks
        if self.rect.bottom < blockgrid.RECT.bottom \
        and (bl[self.gridcell[0]+1][self.gridcell[1]] == None or \
             bl[self.gridcell[0]+1][self.gridcell[1]].state == self.__class__.STATES.FALLING):
        #If we're not at the bottom and there's no block directly below...
            blockgrid.blockstocheck.discard(self)
            self.acceleration[1] = self.__class__.GRAVITY
            self.target          = blockgrid.DIMENSIONS[0] - 1
            self.state           = self.__class__.STATES.START_FALLING
        
    def fall(self):
        '''Falls down.  For the sake of efficiency, blocks work independently
        of the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''
        global blocks
        self.velocity[1]  = min(self.__class__.MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        self.rect.top     = self.position[1] + .5  #Round to the nearest integer
        self.gridcell[0]  = self.rect.centery/self.rect.height
        
        if self.special:
        #If this is a special block...
            self.image = random.choice(block_frames.values()) 
        
        while isinstance(blockgrid.blocks[self.target][self.gridcell[1]], Block):
        #While the target is equal to a space a block currently occupies...
            if self.target < 0:
                sys.exit()
            self.target -= 1
        
        
          
        if self.gridcell[0] == blockgrid.DIMENSIONS[0] - 1:
        #If we've hit the grid's bottom...
            self.rect.bottom = blockgrid.RECT.bottom
            self.position    = list(self.rect.topleft)
            self.state       = self.__class__.STATES.IMPACT
        elif isinstance(blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]], Block):
        #Else if there is a block below us...
            self.rect.bottom = blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]].rect.top
            self.position    = list(self.rect.topleft)
            self.state       = self.__class__.STATES.IMPACT
        
            
    def stop(self):
        #Stop all motion
        global blocks
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.gridcell[0]     = self.rect.centery/self.rect.height #(row, column)
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = self
        
        self.target          = None
        blockgrid.blockstocheck.add(self)  #Might remove later?
        bump.play()
        self.snap()
        self.state           = self.__class__.STATES.ACTIVE
        
        if len([id(b) for b in ingame.BLOCKS if b.state == self.__class__.STATES.ACTIVE]) == len(ingame.BLOCKS):
        #If no blocks are moving...
            blockgrid.update()
        
        if self.special:
        #If this is a special block...
            if self.gridcell[0] < blockgrid.DIMENSIONS[0] - 1:
            #If we're not at the bottom of the grid...
                self.color = blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]].color
                blockgrid.clear_color(self.color)
            else:
                blockgrid.clear_row(self.gridcell[0])
        
    def vanish(self):
        #Maybe if there are any blocks above, they should all start falling.
        self.kill()
        blockgrid.blockstocheck.discard(self)      
        self.position     = None
        self.rect         = None
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        self.gridcell     = None
        self.target       = None
        self.state        = self.__class__.STATES.IDLE
           
    def snap(self):
        self.rect.topleft = (round(self.position[0]/self.image.get_width())*self.image.get_height(),
                             round(self.position[1]/self.image.get_width())*self.image.get_height())
        
    actions = {
                    STATES.IDLE         : None         ,
                    STATES.APPEARING    : 'appear'       ,
                    STATES.ACTIVE       : 'wait'         ,
                    STATES.FALLING      : 'fall'         ,
                    STATES.START_FALLING: 'start_falling',
                    STATES.IMPACT       : 'stop'         ,
                    STATES.DYING        : 'vanish'       ,
              }