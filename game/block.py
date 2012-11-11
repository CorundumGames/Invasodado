import pygame.mixer

import blockgrid
from core import config
from core import color
import ingame
import gameobject

STATES    = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')
FRAME     = pygame.Rect( 0*config.SCALE_FACTOR,
                        32*config.SCALE_FACTOR,
                        16*config.SCALE_FACTOR,
                        16*config.SCALE_FACTOR)
GRAVITY   = .5
MAX_SPEED = 12.0


bump = pygame.mixer.Sound("./sfx/bump.wav")

block_frames = dict([(id(c), color.blend_color(config.SPRITES.subsurface(FRAME).copy(), c)) for c in color.Colors.LIST])


class Block(gameobject.GameObject):
    '''Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    def __init__(self, pos, newcolor):
        gameobject.GameObject.__init__(self)
        self.actions = {
                        STATES.IDLE         : None              ,
                        STATES.APPEARING    : self.appear       ,
                        STATES.ACTIVE       : self.wait         ,
                        STATES.FALLING      : self.fall         ,
                        STATES.START_FALLING: self.start_falling,
                        STATES.IMPACT       : self.stop         ,
                        STATES.DYING        : self.vanish
                        }
        
        self.acceleration[1] = GRAVITY
        self.color           = newcolor
        self.image           = block_frames[id(self.color)]
        self.rect            = pygame.Rect(int(pos[0]/self.image.get_width())*self.image.get_width(),
                                           int(pos[1]/self.image.get_height())*self.image.get_height(),
                                           self.image.get_width(),
                                           self.image.get_height())
        
        
        self.gridcell        = [self.rect.centery/self.rect.height, #(row, column)
                                self.rect.centerx/self.rect.width]
        self.position        = list(self.rect.topleft)
        self.target          = blockgrid.DIMENSIONS[0] - 1
        
        self.state           = STATES.APPEARING
        self.add(ingame.BLOCKS)
        
    def __str__(self):
        return "Block of color " + str(self.color) + " at grid cell " + str(self.gridcell) + " with target " + str(self.target)
        
    def on_collide(self, other):
        pass      
    
    def appear(self):
        self.state = STATES.START_FALLING
            
    def start_falling(self):
        blockgrid.blockstocheck.discard(self)
        for i in xrange(self.gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
                if isinstance(blockgrid.blocks[i][self.gridcell[1]], Block):
                #If this grid cell is occupied...
                    self.target = i - 1
                    break
        
        if self.gridcell[0] > 0 and isinstance(blockgrid.blocks[self.gridcell[0] - 1][self.gridcell[1]], Block):
        #If there is a block above us...
            for i in xrange(self.gridcell[0], 0, -1):
                if isinstance(blockgrid.blocks[i][self.gridcell[1]], Block):
                    blockgrid.blocks[i][self.gridcell[1]].state = STATES.START_FALLING
                else:
                    break
            
        self.state = STATES.FALLING
        
    def wait(self):
        '''Constantly checks to see if this block can fall.  Gets it moving
        if so.
        '''
            
        if self.rect.bottom < blockgrid.RECT.bottom \
        and blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]] == None:
        #If we're not at the bottom and there's no block directly below...
            blockgrid.blockstocheck.discard(self)
            self.acceleration[1] = GRAVITY
            self.target          = blockgrid.DIMENSIONS[0] - 1
            self.state           = STATES.START_FALLING
        
    def fall(self):
        '''Falls down.  For the sake of efficiency, blocks work independently
        of the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''
        self.velocity[1]  = min(MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        self.rect.top     = self.position[1] + .5  #Round to the nearest integer
        self.gridcell[0]  = self.rect.centery/self.rect.height
        

        while isinstance(blockgrid.blocks[self.target][self.gridcell[1]], Block):
        #While the target is equal to a space a block currently occupies...
            self.target -= 1
            
        if self.gridcell[0] == blockgrid.DIMENSIONS[0] - 1:
        #If we've hit the grid's bottom...
            self.rect.bottom = blockgrid.RECT.bottom
            self.position    = list(self.rect.topleft)
            self.state       = STATES.IMPACT
        elif isinstance(blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]], Block):
        #Else if there is a block below us...
            self.rect.bottom = blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]].rect.top
            self.position = list(self.rect.topleft)
            self.state       = STATES.IMPACT
        
            
    def stop(self):
        #Stop all motion
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.gridcell[0]     = self.rect.centery/self.rect.height #(row, column)
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = self
        
        self.target = None
        blockgrid.blockstocheck.add(self)  #Might remove later?
        bump.play()
        self.snap()
        self.state           = STATES.ACTIVE
        
        if len([id(b) for b in ingame.BLOCKS.sprites() if b.state == STATES.ACTIVE]) == len(ingame.BLOCKS.sprites()):
        #If no blocks are moving...
            blockgrid.update()
        
    def vanish(self):
        #Maybe if there are any blocks above, they should all start falling.
        self.kill()
        blockgrid.blockstocheck.discard(self)
        
        
                
        self.position     = None
        self.rect = None
        
        
        
        
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        
        
        self.gridcell     = None
        self.target       = None
        
        
        self.state        = STATES.IDLE
           
    def snap(self):
        self.rect.topleft = (round(self.position[0]/self.image.get_width())*self.image.get_height(),
                             round(self.position[1]/self.image.get_width())*self.image.get_height())