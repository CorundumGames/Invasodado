import os.path
from random import choice

import pygame.mixer

from core            import config
from core            import color
from core            import settings
from core.particles  import ParticlePool, ParticleEmitter
from game.gameobject import GameObject
from game            import blockgrid

### Constants ##################################################################
BLOCK_STATES = ('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')
FRAMES       = [pygame.Rect(32 * i, 160, 32, 32) for i in range(8)]
GRAVITY      =  0.5
MAX_SPEED    = 12.0
################################################################################

### Globals ####################################################################
_blocks_set = set()
_bump       = config.load_sound('bump.wav')
_block_frames    = color.get_colored_objects(FRAMES)
_block_frames_color_blind = color.get_colored_objects(FRAMES,True,True)
################################################################################

### Functions ##################################################################
def clean_up():
    '''
    Removes every Block from memory.
    
    @postcondition: No more Blocks exist, on-screen and off.
    '''
    _blocks_set.clear()
    Block.block_full = False

def get_block(position, newcolor=choice(color.LIST), special=False):
    '''
    Gets a spare Block to add on-screen, creating a new one if there are none.

    @param position: Where to add the new block
    @param newcolor: The color of the new block
    @param special: True if it's a special block dropped by the UFO
    '''
    if not _blocks_set:
    #If we've run out of unused Blocks...
        _blocks_set.add(Block(position, newcolor))

    block          = _blocks_set.pop()
    block.color    = newcolor
    block.position = position
    block._special = special
    block.change_state(Block.STATES.APPEARING)
    return block

################################################################################

class Block(GameObject):
    '''
    Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    STATES         = config.Enum(*BLOCK_STATES)
    block_full     = False
    GROUP          = None
    particle_group = None

    def __init__(self, position, newcolor=choice(color.LIST), special=False):
        GameObject.__init__(self)
        self._anim    = 0
        self.color    = newcolor
        self.current_frame_list = _block_frames_color_blind if settings.color_blind else _block_frames
        self.image              = self.current_frame_list[id(self.color)][0]
        self.position = position
        self.rect     = pygame.Rect(position, self.image.get_size()) #(x, y)
        self._target  = None
        self._special = special
        self.state    = Block.STATES.IDLE

    def __str__(self):
        return ("<Block - color: %s, cell: %s, position: %s, rect: %s, target: %s, state: %i>" %
               (self.color, self.gridcell, self.position, self.rect, self._target, self.state))
        
    def __repr__(self):
        return self.__str__()

    def appear(self):
        self.position     = self.__get_snap()
        self.rect.topleft = self.position
        self.image        = self.current_frame_list[id(self.color)][0]
        self.gridcell     = [
                             self.rect.centerx // self.rect.width,
                             self.rect.centery // self.rect.height,
                            ] #(x, y)
        self._target      = self.__set_target()
        self.emitter      = ParticleEmitter(color.color_particles[id(self.color)], self.rect, 5, Block.particle_group)
        self.change_state(Block.STATES.START_FALLING)
        self.add(Block.GROUP)

    def start_falling(self):
        '''
        Starts the Block falling down.  Only called once before this Block's
        state switches to STATES.FALLING.  Blocks that are falling must not be
        part of matches.
        '''
        self.acceleration[1] = GRAVITY
        blockgrid.check_block(self, False)
        self.__set_target()

        if self.gridcell[1]:
        #If we're not at the top of the grid...
            block_above = blockgrid.blocks[self.gridcell[0]][self.gridcell[1] - 1]
            if block_above:
            #If there's at least one block above us...
                assert isinstance(block_above, Block), \
                "%s expected a Block, got a %s" % (self, block_above)

                for i in blocks[self.gridcell[0]]:
                #For all grid cells above us...
                    if i and not i.velocity[1]:
                    #If this is a block that's not moving...
                        i.change_state(Block.STATES.START_FALLING)
                    else:
                        break

        self.change_state(Block.STATES.FALLING)

    def fall(self):
        '''
        Falls down.  For the sake of efficiency, blocks work independently of
        the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''
        gridcell = self.gridcell
        position = self.position
        rect     = self.rect
        
        self.velocity[1] = min(MAX_SPEED, self.velocity[1] + self.acceleration[1])
        position[1]     += self.velocity[1]
        rect.top         = position[1] + 0.5 #Round to the nearest integer
        gridcell[1]      = self.rect.centery // self.rect.height
        self.emitter.rect.topleft = rect.topleft

        if self._anim < len(FRAMES) - 1:
        #If we haven't hit the last frame of animation...
            self._anim += 1
            self.image  = self.current_frame_list[id(self.color)][self._anim]

        if self._special:
        #If this is a _special block...
            self.image = self.current_frame_list[id(choice(color.LIST))][self._anim]

        self.__set_target()

        if self._target is not None and self._target < 1:
        #If we go past the top of the screen...
            Block.block_full = True
        
        if rect.bottom >= blockgrid.RECT.bottom:
        #If we've hit the bottom of the grid...
            rect.bottom     = blockgrid.RECT.bottom
            position[1]     = rect.top
            self.change_state(Block.STATES.IMPACT)
        elif self.gridcell[1] + 1 < blockgrid.SIZE[1]:
        #Else if it was another block...
            below = blockgrid.blocks[gridcell[0]][gridcell[1] + 1]
            if below and rect.bottom >= below.rect.top:
            #If we've gone past the block below...
                rect.bottom     = below.rect.top
                position[1]     = rect.top
                self.change_state(Block.STATES.IMPACT)
            assert isinstance(below, Block) or below is None, \
            "A %s is trying to collide with a stray %s!" % (self, below)
        
        assert rect.colliderect(blockgrid.RECT) \
        and blockgrid.RECT.collidepoint(position) \
        and self.state == Block.STATES.FALLING, \
        "An active %s has somehow left the field!" % self

    def wait(self):
        '''
        Constantly checks to see if this block can fall.
        '''
        gridcell = self.gridcell

        if self.rect.bottom < blockgrid.RECT.bottom:
        #If we're not at the bottom of the grid...
            block_below = blockgrid.blocks[gridcell[0]][gridcell[1] + 1]
            if not block_below or block_below.velocity[1]:
            #If there's no block directly below...
                blockgrid.check_block(self, False)
                self.acceleration[1] = GRAVITY
                self.change_state(Block.STATES.START_FALLING)
                
        if __debug__ and self.rect.collidepoint(pygame.mouse.get_pos()):
            print(self)

    def stop(self):
        '''
        Handles the Block when it hits the bottom of the grid or another block.
        Changes velocity, plays sounds, etc.
        '''
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.position        = self.__get_snap()
        self.rect.topleft    = self.position
        self.gridcell[1]     = self.rect.centery // self.rect.height #(row, col)
        self._target         = None
        self.state           = Block.STATES.ACTIVE
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = self

        blockgrid.check_block(self, True)
        _bump.play()
        #blockgrid.update()
        
        if self._special:
        #If this is a special block...
            if self.gridcell[1] < blockgrid.SIZE[1] - 1:
            #If we're not at the bottom of the grid...
                self.color = blockgrid.blocks[self.gridcell[0]][self.gridcell[1]+ 1].color
                blockgrid.clear_color(self.color)
            else:
                blockgrid.clear_row(self.gridcell[1])
                

    def vanish(self):
        blockgrid.check_block(self, False)
        self.emitter.burst(20)
        self.kill()
        
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        self._anim                                 = 0
        self.position                              = [-300.0, -300.0]
        self.rect.topleft                          = self.position
        self.gridcell                              = None
        self._target                               = None
        self.change_state(Block.STATES.IDLE)
        self.__replace()
        
    def __replace(self):
        '''
        Puts this Block back in the set of spares.
        
        @postcondition: This Block is ready to be recycled.
        '''
        _blocks_set.add(self)
        
    def __set_target(self):
        '''
        Determines which row this block should fall down to.
        '''
        for i in range(self.gridcell[1] + 1, blockgrid.SIZE[1]):
        #For all grid cells below this one...
            other = blockgrid.blocks[self.gridcell[0]][i]
            if other and not other.velocity[1]:
            #If this grid cell is occupied...
                self._target = i - 1
                break
        
        return self._target
    
    def __get_snap(self):
        '''
        Returns a position list that snaps this block to the grid.
        '''
        size = self.image.get_size()
        return [
                round(self.position[0] / size[0]) * size[0],
                round(self.position[1] / size[1]) * size[1]
               ]
        
    actions = {
                STATES.IDLE         : None           ,
                STATES.APPEARING    : 'appear'       ,
                STATES.ACTIVE       : 'wait'         ,
                STATES.FALLING      : 'fall'         ,
                STATES.START_FALLING: 'start_falling',
                STATES.IMPACT       : 'stop'         ,
                STATES.DYING        : 'vanish'       ,
              }