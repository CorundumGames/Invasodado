import os.path
from random import choice, uniform

import pygame.mixer

from core            import config
from core            import color
from core.particles  import ParticlePool, ParticleEmitter
from game.gameobject import GameObject
from game            import blockgrid


FRAMES  = [pygame.Rect(32 * i, 160, 32, 32) for i in range(8)]
GRAVITY = 0.5

_blocks_set = set()
_bump       = pygame.mixer.Sound(os.path.join('sfx', '_bump.wav'))

_block_frames    = color.get_colored_objects(FRAMES)
_color_particles = color.get_colored_objects([pygame.Rect(4, 170, 4, 4)], False)


def _bp_move(self):
    '''
    Moves this Particle a little bit this frame.
    '''
    position = self.position
    velocity = self.velocity

    velocity[1]      += self.acceleration[1]
    position[0]      += velocity[0]
    position[1]      += velocity[1]
    self.rect.topleft = (position[0] + .5, position[1] + .5)

def _bp_appear(self):
    '''
    Initializes the location and velocity for this Particle.
    '''
    self.acceleration[1] = GRAVITY
    self.velocity        = [uniform(-5, 5), uniform(-1, -3)]

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
    @param _special: True if it's a special block dropped by the UFO
    '''
    if not _blocks_set:
    #If we've run out of unused Blocks...
        _blocks_set.add(Block(position, newcolor))

    block          = _blocks_set.pop()
    block.color    = newcolor
    block.position = position
    block._special = special
    block.state    = Block.STATES.APPEARING
    return block

_block_particles  = dict([(id(c), ParticlePool(_color_particles[id(c)][0], _bp_move, _bp_appear)) for c in color.LIST])

class Block(GameObject):
    '''
    Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    block_full     = False
    collisions     = None
    GROUP          = None
    particle_group = None
    GRAVITY        = 0.5
    MAX_SPEED      = 12.0
    STATES         = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')

    def __init__(self, position, newcolor=choice(color.LIST), special=False):
        GameObject.__init__(self)
        self._anim    = 0
        self.color    = newcolor
        self.image    = _block_frames[id(self.color)][0]
        self.position = position

        size = self.image.get_size()
        self.rect     = pygame.Rect(
                                    [
                                     round(position[0] / size[0]) * size[0],
                                     round(position[1] / size[1]) * size[1]
                                    ],
                                    size
                                   )
        self._target  = None
        self._special = special
        self.state    = Block.STATES.IDLE

    def __str__(self):
        return ("Block of color %s at grid cell %s with _target %s" %
               (self.color, self.gridcell, self._target))

    def appear(self):
        self.image    = _block_frames[id(self.color)][0]

        size = self.image.get_size()
        self.position     = [
                             round(self.position[0] / size[0]) * size[0],
                             round(self.position[1] / size[1]) * size[1]
                            ]
        self.rect.topleft = self.position
        self.gridcell     = [
                             self.rect.centery / self.rect.height, 
                             self.rect.centerx / self.rect.width
                            ]  #(row, column)
        self._target      = blockgrid.DIMENSIONS[0] - 1
        self.emitter      = ParticleEmitter(_block_particles[id(self.color)], self.rect, 5, Block.particle_group)
        self.state        = Block.STATES.START_FALLING
        self.add(Block.GROUP)

    def start_falling(self):
        blocks   = blockgrid.blocks
        gridcell = self.gridcell

        self.acceleration[1] = Block.GRAVITY
        blockgrid.blocks_to_check.discard(self)
        for i in xrange(gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
            other = blocks[i][gridcell[1]]
            if other and other.state in {Block.STATES.ACTIVE, Block.STATES.IMPACT}:
            #If this grid cell is occupied...
                self._target = i - 1
                break

        block_above = blocks[gridcell[0] - 1][gridcell[1]]
        if gridcell[0] and block_above:
        #If there's at least one block above us...
            assert isinstance(block_above, Block), \
            "%s expected a Block, got a %s" % (self, block_above)

            for i in reversed(blocks):
            #For all grid cells above us...
                if i[gridcell[1]]:
                #If this is actually a block...
                    i[gridcell[1]].state = Block.STATES.START_FALLING
                else:
                    break

        self.state = Block.STATES.FALLING

    def fall(self):
        '''
        Falls down.  For the sake of efficiency, blocks work independently of
        the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''
        blocks   = blockgrid.blocks
        gridcell = self.gridcell
        rect     = self.rect
        self.velocity[1]  = min(Block.MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        rect.top          = self.position[1] + .5 #Round to the nearest integer
        gridcell[0]       = rect.centery / rect.height
        self.emitter.rect.topleft = rect.topleft

        if self._anim < len(FRAMES) - 1:
        #If we haven't hit the last frame of animation...
            self._anim += 1
            self.image  = _block_frames[id(self.color)][self._anim]

        if self._special:
        #If this is a _special block...
            self.image = choice(_block_frames.values())[self._anim]

        for i in xrange(gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
            other = blocks[i][gridcell[1]]
            if other and other.state in {Block.STATES.ACTIVE, Block.STATES.IMPACT}:
            #If this grid cell is occupied...
                self._target = i - 1
                break

        if self._target is not None and self._target < 1:
        #If we go past the top of the screen...
            Block.block_full = True
        
        if gridcell[0] >= blockgrid.DIMENSIONS[0] - 1:
        #If we've hit the bottom of the grid...
            rect.bottom   = blockgrid.RECT.bottom
            self.position = list(rect.topleft)
            self.state    = Block.STATES.IMPACT
        elif blocks[gridcell[0] + 1][gridcell[1]]:
        #Else if it was another block...
            below         = blocks[gridcell[0] + 1][gridcell[1]]
            rect.bottom   = below.rect.top
            self.position = list(rect.topleft)
            self.state    = Block.STATES.IMPACT
            assert isinstance(below, Block) or below is None, \
            "A %s is trying to collide with a stray %s!" % (self, below)
        
        assert rect.colliderect(blockgrid.RECT) and blockgrid.RECT.collidepoint(self.position), \
        "An active %s has somehow left the field!" % self

    def wait(self):
        '''
        Constantly checks to see if this block can fall.
        '''
        blocks   = blockgrid.blocks
        gridcell = self.gridcell

        if self.rect.bottom < blockgrid.RECT.bottom:
        #If we're not at the bottom...
            block_below = blocks[gridcell[0] + 1][gridcell[1]]
            if not block_below or block_below.state not in {Block.STATES.ACTIVE, Block.STATES.IMPACT}:
            #If there's no block directly below...
                blockgrid.blocks_to_check.discard(self)
                self.acceleration[1] = GRAVITY
                self.state           = Block.STATES.START_FALLING

    def stop(self):
        gridcell = self.gridcell

        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        gridcell[0]          = self.rect.centery / self.rect.height #(row, col)
        self._target         = None
        print blockgrid.blocks[gridcell[0]][gridcell[1]]
        blockgrid.blocks[gridcell[0]][gridcell[1]] = self

        blockgrid.blocks_to_check.add(self)
        _bump.play()
        blockgrid.update()

        if self._special:
        #If this is a special block...
            if gridcell[0] < blockgrid.DIMENSIONS[0] - 1:
            #If we're not at the bottom of the grid...
                self.color = blockgrid.blocks[gridcell[0]+1][gridcell[1]].color
                blockgrid.clear_color(self.color)
            else:
                blockgrid.clear_row(gridcell[0])
        self.state = Block.STATES.ACTIVE

    def vanish(self):
        self.emitter.burst(20)
        self._anim                                           = 0
        self.kill()
        blockgrid.blocks_to_check.discard(self)
        self.position                                        = [-300, -300]
        self.rect.topleft                                    = self.position
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        self.gridcell                                        = None
        self._target                                         = None
        self.state                                           = Block.STATES.IDLE
        _blocks_set.add(self)

    actions = {
                STATES.IDLE         : None           ,
                STATES.APPEARING    : 'appear'       ,
                STATES.ACTIVE       : 'wait'         ,
                STATES.FALLING      : 'fall'         ,
                STATES.START_FALLING: 'start_falling',
                STATES.IMPACT       : 'stop'         ,
                STATES.DYING        : 'vanish'       ,
              }