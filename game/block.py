import itertools
import random

import pygame.mixer

import core.color  as color
import core.config as config
import core.particles as particles

import blockgrid
import gameobject
import ingame

FRAMES  = [pygame.Rect(32 * i, 160, 32, 32) for i in range(8)]
GRAVITY = 0.5

blocks_set = set()
bump = pygame.mixer.Sound("./sfx/bump.wav")

block_frames    = config.get_colored_objects(FRAMES)
particle_colors = config.get_colored_objects([pygame.Rect(4, 170, 4, 4)], False)


def _block_particle_move(self):
    p = self.position

    self.velocity[1] += self.acceleration[1]
    p[0] += self.velocity[0]
    p[1] += self.velocity[1]
    self.rect.topleft = (p[0] + .5, p[1] + .5)

def _block_particle_appear(self):
    self.acceleration[1] = GRAVITY
    self.velocity        = [random.uniform(-5, 5), random.uniform(-1, -3)]

def clean_up():
    blocks_set.clear()

def get_block(pos, newcolor = random.choice(color.LIST), special = False):
    if len(blocks_set) == 0:
        blocks_set.add(Block(pos, newcolor))

    b          = blocks_set.pop()
    b.color    = newcolor
    b.position = pos
    b.special  = special
    b.state    = Block.STATES.APPEARING
    return b

block_particles  = dict([(id(c), particles.ParticlePool(particle_colors[id(c)][0], _block_particle_move, _block_particle_appear)) for c in color.LIST])

class Block(gameobject.GameObject):
    '''
    Blocks are left by enemies when they're killed.  Match three of the same
    color, and they'll disappear.
    '''
    block_full = False
    collisions = None
    GRAVITY    = 0.5
    MAX_SPEED  = 12.0
    STATES     = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'START_FALLING', 'FALLING', 'IMPACT', 'DYING')


    def __init__(self, pos, newcolor = random.choice(color.LIST), specialblock = False):
        gameobject.GameObject.__init__(self)
        self.anim     = 0
        self.color    = newcolor
        self.image    = block_frames[id(self.color)][0]
        self.position = pos

        size = self.image.get_size()
        self.rect     = pygame.Rect(round(pos[0] / size[0]) * size[0],
                                    round(pos[1] / size[1]) * size[1],
                                    size[0],
                                    size[1]
                                   )
        self.special  = specialblock
        self.state    = self.__class__.STATES.IDLE


    def __str__(self):
        return "Block of color %s at grid cell %s with target %i" % (self.color, self.gridcell, self.target)

    def appear(self):
        self.image    = block_frames[id(self.color)][0]

        size = self.image.get_size()
        self.position     = [round(self.position[0] / size[0]) * size[0],
                             round(self.position[1] / size[1]) * size[1]
                             ]
        self.rect.topleft = self.position
        self.position     = list(self.rect.topleft)
        self.gridcell     = [self.rect.centery / self.rect.height, #(row, column)
                             self.rect.centerx / self.rect.width]
        self.target       = blockgrid.DIMENSIONS[0] - 1
        self.emitter      = particles.ParticleEmitter(block_particles[id(self.color)], self.rect, 5, ingame.BLOCKS)
        self.state        = self.__class__.STATES.START_FALLING
        self.add(ingame.BLOCKS)

    def start_falling(self):
        self.acceleration[1] = GRAVITY
        bl = blockgrid.blocks
        blockgrid.blockstocheck.discard(self)
        for i in xrange(self.gridcell[0] + 1, blockgrid.DIMENSIONS[0]):
        #For all grid cells below this one...
                if isinstance(bl[i][self.gridcell[1]], Block) \
                and (blockgrid.blocks[i][self.gridcell[1]].state is not self.__class__.STATES.FALLING):
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
        '''
        Constantly checks to see if this block can fall.
        '''
        bl = blockgrid.blocks
        gc = self.gridcell
        if self.rect.bottom < blockgrid.RECT.bottom \
        and (bl[gc[0] + 1][gc[1]] == None or \
             bl[gc[0] + 1][gc[1]].state == self.__class__.STATES.FALLING):
        #If we're not at the bottom and there's no block directly below...
            blockgrid.blockstocheck.discard(self)
            self.target = blockgrid.DIMENSIONS[0] - 1
            self.acceleration[1] = GRAVITY
            self.state = self.__class__.STATES.START_FALLING

    def fall(self):
        '''
        Falls down.  For the sake of efficiency, blocks work independently
        of the collision detection system, since they're only going to move
        vertically, and only depend on other blocks for collisions.
        '''

        self.velocity[1]  = min(self.__class__.MAX_SPEED, self.velocity[1] + self.acceleration[1])
        self.position[1] += self.velocity[1]
        self.rect.top     = self.position[1] + .5  #Round to the nearest integer
        self.gridcell[0]  = self.rect.centery / self.rect.height
        self.emitter.rect.topleft = self.rect.topleft

        if self.anim < len(FRAMES) - 1:
            self.anim += 1
            self.image = block_frames[id(self.color)][self.anim]

        if self.special:
        #If this is a special block...
            self.image = random.choice(block_frames.values())[self.anim]

        while self.target >= 0 and isinstance(blockgrid.blocks[self.target][self.gridcell[1]], Block) \
        and not (blockgrid.blocks[self.target][self.gridcell[1]].state == self.__class__.STATES.FALLING):
        #While the target is equal to a space a block currently occupies...
                self.target -= 1

        if self.target < 1 and not (self.target == None):
            print(self.target)
            self.__class__.block_full = True



        if self.gridcell[0] == blockgrid.DIMENSIONS[0] - 1 or \
        isinstance(blockgrid.blocks[self.gridcell[0] + 1][self.gridcell[1]], Block):
        #If we've hit something...
            if self.gridcell[0] == blockgrid.DIMENSIONS[0] - 1:
            #If that something was the grid's bottom...
                self.rect.bottom = blockgrid.RECT.bottom
            else:
            #Otherwise it was another block.
                self.rect.bottom = blockgrid.blocks[self.gridcell[0] + 1][self.gridcell[1]].rect.top

            self.position = list(self.rect.topleft)
            self.state    = self.__class__.STATES.IMPACT



    def stop(self):
        #Stop all motion
        self.acceleration[1] = 0.0
        self.velocity[1]     = 0.0
        self.gridcell[0]     = self.rect.centery / self.rect.height #(row, column)
        blockgrid.blocks[self.gridcell[0]][self.gridcell[1]] = self

        self.target = None
        blockgrid.blockstocheck.add(self)  #Might remove later?
        bump.play()
        self.snap()
        self.state = self.__class__.STATES.ACTIVE

        #Update the blockgrid
        blockgrid.update()

        if self.special:
        #If this is a special block...
            if self.gridcell[0] < blockgrid.DIMENSIONS[0] - 1:
            #If we're not at the bottom of the grid...
                self.color = blockgrid.blocks[self.gridcell[0] + 1][self.gridcell[1]].color
                blockgrid.clear_color(self.color)
            else:
                blockgrid.clear_row(self.gridcell[0])

    def vanish(self):
        self.emitter.burst(20)
        self.anim                                            = 0
        self.remove(ingame.BLOCKS)
        blockgrid.blockstocheck.discard(self)
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

