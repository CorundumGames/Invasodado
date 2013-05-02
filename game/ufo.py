from math import sin
import os.path
from random import choice, uniform, expovariate
from functools import lru_cache

import pygame

from core            import color
from core            import config
from core.particles  import ParticleEmitter
from game.block      import get_block
from game.gameobject import GameObject

### Constants ##################################################################
AVG_WAIT   = 9000 #Expected time in frames between UFO appearance
DEATH      = config.load_sound('ufo_explosion.wav')
FRAMES     = tuple(
              pygame.Rect(64 * (i % 4), 192 + 32 * (i // 4), 64, 32)
              for i in range(10, -1, -1)
             )
INVADE     = config.load_sound('ufo.wav')
START_POS  = (640, 16)
UFO_FRAMES = color.get_colored_objects(FRAMES)
UFO_STATES = ('IDLE', 'APPEARING', 'ACTIVE', 'DYING', 'LEAVING', 'LOWERING', 'GAMEOVER')
################################################################################

class UFO(GameObject):
    STATES      = config.Enum(*UFO_STATES)
    GROUP       = None
    BLOCK_GROUP = None

    def __init__(self):
        super().__init__()
        self._anim    = 0.0
        self.column   = None
        self.current_frame_list = UFO_FRAMES
        self.image    = config.get_sprite(FRAMES[0])
        self.odds     = expovariate(AVG_WAIT)
        self.position = list(START_POS)
        self.rect     = pygame.Rect(START_POS, self.image.get_size())
        self.state    = UFO.STATES.IDLE
        self.emitter  = ParticleEmitter(color.random_color_particles, self.rect)

        del self.acceleration

    def appear(self):
        '''
        Appear on-screen, but not for very long!
        '''
        INVADE.play(-1)
        self.position     = list(START_POS)
        self.rect.topleft = list(START_POS)
        self.change_state(UFO.STATES.ACTIVE)
        self.velocity[0]  = -2.0

    def move(self):
        '''
        Move left on the screen, and oscillate up and down.
        '''
        position = self.position
        rect     = self.rect
            
        self._anim += 0.5
        self.image  = UFO_FRAMES[id(choice(color.LIST))       ] \
                                [int(self._anim) % len(FRAMES)]
        position[0] += self.velocity[0]
        position[1] += sin(self._anim/4)
        rect.topleft = (position[0] + .5, position[1] + .5)

        if rect.right < 0:
        #If we've gone past the left edge of the screen...
            self.change_state(UFO.STATES.LEAVING)

    def die(self):
        '''
        Vanish and release a special Block that clears lots of other Blocks.
        '''
        self.emitter.rect = self.rect
        self.emitter.burst(30)
        DEATH.play()
        UFO.BLOCK_GROUP.add(get_block([self.rect.centerx, 0], special=True))
        self.change_state(UFO.STATES.LEAVING)

    def leave(self):
        INVADE.stop()
        self.velocity[0]  = 0
        self.position     = list(START_POS)
        self.rect.topleft = START_POS
        self.change_state(UFO.STATES.IDLE)

    def wait(self):
        '''
        Wait off-screen, and only come back with a specific probability.
        '''
        if uniform(0, 1) < self.odds:
        #With a certain probability...
            self.odds = expovariate(AVG_WAIT)
            self.change_state(UFO.STATES.APPEARING)

    actions = {
                STATES.IDLE     : 'wait'  ,
                STATES.APPEARING: 'appear',
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.LEAVING  : 'leave' ,
                STATES.GAMEOVER : None    ,
              }