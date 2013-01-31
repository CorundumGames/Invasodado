import os.path
from random import choice, uniform

import pygame.mixer

from core           import color
from core.particles import ParticlePool, ParticleEmitter
from game.gameobject import GameObject
from game import blockgrid


FRAMES  = [pygame.Rect(32 * i, 160, 32, 32) for i in range(8)]
GRAVITY = 0.5

blocks_set = set()
bump       = pygame.mixer.Sound(os.path.join('sfx', 'bump.wav'))

block_frames    = color.get_colored_objects(FRAMES)
particle_colors = color.get_colored_objects([pygame.Rect(4, 170, 4, 4)], False)


def _block_particle_move(self):
    position = self.position
    velocity = self.velocity

    velocity[1]      += self.acceleration[1]
    position[0]      += velocity[0]
    position[1]      += velocity[1]
    self.rect.topleft = (position[0] + .5, position[1] + .5)

def _block_particle_appear(self):
    self.acceleration[1] = GRAVITY
    self.velocity        = [uniform(-5, 5), uniform(-1, -3)]

def clean_up():
    blocks_set.clear()
    Block.block_full = False

def get_block(position, newcolor=choice(color.LIST), special=False):
    '''
    Gets a spare blck to add on-screen, creating a new one if none are available.

    @param position: Where to add the new block
    @param newcolor: The color of the new block
    @param special: True if it's a special block dropped by the UFO
    '''
    if not blocks_set:
    #If we've run out of unused Blocks...
        blocks_set.add(Block(position, newcolor))

    block          = blocks_set.pop()
    block.color    = newcolor
    block.position = position
    block.special  = special
    block.state    = Block.STATES.APPEARING
    return block

block_particles  = dict([(id(c), ParticlePool(particle_colors[id(c)][0], _block_particle_move, _block_particle_appear)) for c in color.LIST])

class Block(GameObject):
    '''
    Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    from core import config
    block_full = False
    collisions = None
    group      = None
    GRAVITY    = 0.5
    MAX_SPEED  = 12.0
    STATES     = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')


    def __init__(self, position, newcolor=choice(color.LIST), special=False):
        GameObject.__init__(self)
        self.anim     = 0
        self.color    = newcolor
        self.image    = block_frames[id(self.color)][0]
        self.position = position

        size = self.image.get_size()
        self.rect     = pygame.Rect([
                                     round(position[0] / size[0]) * size[0],
                                     round(position[1] / size[1]) * size[1]
                                    ],
                                    size
                                   )

        self.special  = special
        self.state    = Block.STATES.IDLE

    def __str__(self):
        return ("Block of color %s at grid cell %s with target %i" %
               (self.color, self.gridcell, self.target))

    def appear(self):
        self.image    = block_frames[id(self.color)][0]

        size = self.image.get_size()
        self.position     = [
                             round(self.position[0] / size[0]) * size[0],
                             round(self.position[1] / size[1]) * size[1]
                            ]
        self.rect.topleft = self.position
        self.gridcell     = [
                             self.rect.centery / self.rect.height, #(row, column)
                             self.rect.centerx / self.rect.width
                            ]
        self.target       = blockgrid.DIMENSIONS[0] - 1
        self.emitter      = ParticleEmitter(block_particles[id(self.color)], self.rect, 5, Block.group)
        self.state        = Block.STATES.START_FALLING
        self.add(Block.group)

    def start_falling(self):
        blocks   = blockgrid.blocks
        gridcell = self.gridcell

        self.acceleration[1] = GRAVITY
        blockgrid.blocks_to_check.discard(self)
        for i in xrange(gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
            other = blocks[i][gridcell[1]]
            if (other and other.state != Block.STATES.FALLING):
            #If this grid cell is occupied...
                self.target = i - 1
                break

        block_above = blocks[gridcell[0] - 1][gridcell[1]]
        if gridcell[0] and block_above:
        #If there's at least one block above us...
            assert isinstance(block_above, Block), \
            "%s expected a Block, got a %s" % (self, block_above)

            for i in xrange(gridcell[0], 0, -1):
            #For all grid cells above us...
                #if isinstance(blocks[i][gridcell[1]], Block):
                if blocks[i][gridcell[1]]:
                #If this is actually a block...
                    blocks[i][gridcell[1]].state = Block.STATES.START_FALLING
                else:
                    break

        self.state = Block.STATES.FALLING

    def wait(self):
        '''
        Constantly checks to see if this block can fall.
        '''
        blocks   = blockgrid.blocks
        gridcell = self.gridcell

        if self.rect.bottom < blockgrid.RECT.bottom:
        #If we're not at the bottom...
            block_below = blocks[gridcell[0] + 1][gridcell[1]]
            if not block_below or block_below.state == Block.STATES.FALLING:
            #If there's no block directly below...
                blockgrid.blocks_to_check.discard(self)
                self.target          = blockgrid.DIMENSIONS[0] - 1
                self.acceleration[1] = GRAVITY
                self.state           = Block.STATES.START_FALLING

    def fall(self):
        '''
        Falls down.  For the sake of efficiency, blocks work independently
        of the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''
        blocks   = blockgrid.blocks
        gridcell = self.gridcell
        rect     = self.rect

        self.velocity[1]  = min(Block.MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        rect.top          = self.position[1] + .5  #Round to the nearest integer
        gridcell[0]       = rect.centery / rect.height
        self.emitter.rect.topleft = rect.topleft

        if self.anim < len(FRAMES) - 1:
        #If we haven't hit the last frame of animation...
            self.anim += 1
            self.image = block_frames[id(self.color)][self.anim]

        if self.special:
        #If this is a special block...
            self.image = choice(block_frames.values())[self.anim]

        #while self.target >= 0 and isinstance(blocks[self.target][gridcell[1]], Block) \
        #and (blocks[self.target][gridcell[1]].state != Block.STATES.FALLING):
        while self.target >= 0:
         #While the target is equal to a space a block currently occupies...
            below = blocks[self.target][gridcell[1]]
            if below and below.state != Block.STATES.FALLING:
                self.target -= 1
            else:
                break

        if self.target < 1:
        #If we go past the top of the screen...
            Block.block_full = True

        if gridcell[0] == blockgrid.DIMENSIONS[0] - 1 or blocks[gridcell[0] + 1][gridcell[1]]:
        #If we've hit something...
            if gridcell[0] == blockgrid.DIMENSIONS[0] - 1:
            #If that something was the grid's bottom...
                rect.bottom = blockgrid.RECT.bottom
            else:
            #Otherwise it was another block.
                assert isinstance(blocks[gridcell[0] + 1][gridcell[1]], Block) or blocks[gridcell[0] + 1][gridcell[1]] is None, \
                "A %s is trying to collide with a stray %s!" % \
                (self, blocks[gridcell[0] + 1][gridcell[1]])
                rect.bottom = block_below.rect.top

            self.position = list(rect.topleft)
            self.state    = Block.STATES.IMPACT

        assert rect.colliderect(blockgrid.RECT), \
        "An active block %s has somehow left the field!" % self

    def stop(self):
        gridcell = self.gridcell

        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        gridcell[0]          = self.rect.centery / self.rect.height #(row, column)
        self.target          = None
        self.state           = Block.STATES.ACTIVE
        blockgrid.blocks[gridcell[0]][gridcell[1]] = self

        blockgrid.blocks_to_check.add(self)
        bump.play()
        self.snap()
        blockgrid.update()

        if self.special:
        #If this is a special block...
            if gridcell[0] < blockgrid.DIMENSIONS[0] - 1:
            #If we're not at the bottom of the grid...
                self.color = blockgrid.blocks[gridcell[0] + 1][gridcell[1]].color
                blockgrid.clear_color(self.color)
            else:
                blockgrid.clear_row(gridcell[0])

    def vanish(self):
        self.emitter.burst(20)
        self.anim                                            = 0
        self.remove(ingame.BLOCKS)
        blockgrid.blocks_to_check.discard(self)
        self.position                                        = [-300, -300]
        self.rect.topleft                                    = self.position
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = None
        self.gridcell                                        = None
        self.target                                          = None
        self.state                                           = Block.STATES.IDLE
        blocks_set.add(self)

    def snap(self):
        self.rect.topleft = (round(self.position[0] / self.image.get_width()) * self.image.get_height(),
                             round(self.position[1] / self.image.get_width()) * self.image.get_height())

    actions = {
                STATES.IDLE         : None           ,
                STATES.APPEARING    : 'appear'       ,
                STATES.ACTIVE       : 'wait'         ,
                STATES.FALLING      : 'fall'         ,
                STATES.START_FALLING: 'start_falling',
                STATES.IMPACT       : 'stop'         ,
                STATES.DYING        : 'vanish'       ,
              }