import pygame.mixer

import blockgrid
from core import config
from core import color
import ingame
import gameobject

STATES    = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'FALLING', 'IMPACT', 'DYING')
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
                        STATES.IDLE     : None          ,
                        STATES.APPEARING: NotImplemented,
                        STATES.ACTIVE   : self.wait     ,
                        STATES.FALLING  : self.fall     ,
                        STATES.IMPACT   : self.stop     ,
                        STATES.DYING    : self.vanish
                        }
        
        self.acceleration[1] = GRAVITY
        self.color           = newcolor
        self.image           = block_frames[id(self.color)]
        self.rect            = pygame.Rect(int(pos[0]/self.image.get_width())*self.image.get_width(),
                                           int(pos[1]/self.image.get_height())*self.image.get_height(),
                                           self.image.get_width(),
                                           self.image.get_height())
        
        
        self.gridcell        = [self.rect.y/self.rect.height, #(row, column)
                                self.rect.x/self.rect.width]
        self.position        = list(self.rect.topleft)
        
        self.state           = STATES.FALLING
        self.add(ingame.BLOCKS)
        
    def __str__(self):
        return "Block of color " + str(self.color) + " at grid cell" + str(self.gridcell)
        
    def on_collide(self, other):
        if isinstance(other, Block) and self.state == STATES.FALLING\
        and other.gridcell == [self.gridcell[0]+1, self.gridcell[1]]:
        #If we hit a block, we're falling, and the block we hit is a cell below us...
            self.block_below = other
            self.rect.bottom = other.rect.top
            self.state       = STATES.IMPACT
        pass      
            
    def wait(self):
        '''Constantly checks to see if this block can fall.  Gets it moving
        if so.
        '''
        if self.rect.bottom < blockgrid.RECT.bottom\
        and self.rect.bottom != blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]].rect.top:
        #If we're not at the bottom and there's no block directly below...
            blockgrid.blockstocheck.discard(self)
            self.acceleration[1] = GRAVITY
            self.state           = STATES.FALLING
        
    def fall(self):
        self.velocity[1]  = min(MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        self.rect.top     = round(self.position[1])
        self.gridcell[0]  = self.rect.centery/self.rect.height #(row, column)
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = self
        
        if self.gridcell[0] < blockgrid.DIMENSIONS[0]-1:
        #If we're not at the bottom of the grid...
            if isinstance(blockgrid.blocks[self.gridcell[0]+1][self.gridcell[1]], Block):  #This is always returning false.  It always registers as None
            #If there is a block below us...
                print "france"
                self.rect.bottom = blockgrid.blocks[self.gridcell[0]-1][self.gridcell[1]].rect.top
                self.state       = STATES.IMPACT
        
        if self.rect.bottom > blockgrid.RECT.bottom:  #@UndefinedVariable
        #If we've hit the grid's bottom...
            self.rect.bottom = blockgrid.RECT.bottom
            self.state       = STATES.IMPACT
            
    def stop(self):
        #Stop all motion
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.gridcell[0]     = self.rect.centery/self.rect.height #(row, column)
        blockgrid.blockstocheck.add(self)  #Might remove later?
        bump.play()
        self.state           = STATES.ACTIVE
        
        blockgrid.update()
        
    def vanish(self):
        self.kill()
        blockgrid.blockstocheck.discard(self)
        self.position     = [-300.0, -300.0]
        self.rect.topleft = self.position
        self.gridcell     = None
        self.state        = STATES.IDLE
           
    def snap(self):
        self.rect.topleft = (round(self.position[0]/self.image.get_width())*self.image.get_height(),
                             round(self.position[1]/self.image.get_width())*self.image.get_height())