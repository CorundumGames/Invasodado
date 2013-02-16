from math import sin
import os.path
from random import choice, uniform

import pygame

from core       import color
from core       import config
from game.block import get_block

from game.gameobject import GameObject#

FRAMES     = [
              pygame.Rect(64 * (i % 4), 192 + 32 * (i / 4), 64, 32)
              for i in range(10, -1, -1)
             ]
START_POS  = (640, 16)
UFO_FRAMES = color.get_colored_objects(FRAMES)

class UFO(GameObject):
    STATES      = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'DYING', 'LEAVING')
    invade      = pygame.mixer.Sound(os.path.join('sfx', 'ufo.wav'))
    GROUP       = None
    BLOCK_GROUP = None
    #The sound the UFO makes as it flies across the screen

    def __init__(self):
        GameObject.__init__(self)
        self._anim    = 0.0
        self.image    = config.SPRITES.subsurface(FRAMES[0]).copy()
        self.odds     = .0001
        self.position = list(START_POS)
        self.rect     = pygame.Rect(START_POS, self.image.get_size())
        self.state    = UFO.STATES.IDLE

        del self.acceleration

    def appear(self):
        '''
        Appear on-screen, but not for very long!
        '''
        self.position     = list(START_POS)
        self.rect.topleft = list(START_POS)
        self.state        = UFO.STATES.ACTIVE
        self.velocity[0]  = -1.1

    def move(self):
        '''
        Move left on the screen, and oscillate up and down.
        '''
        position = self.position
        rect     = self.rect

        #UFO_GROUP.invade.play()
        self._anim += 0.5
        self.image  = UFO_FRAMES[id(choice(color.LIST))       ] \
                                [int(self._anim) % len(FRAMES)]
        position[0] += self.velocity[0]
        position[1] += sin(self._anim/4)
        rect.topleft = (position[0] + .5, position[1] + .5)

        if rect.right < 0:
        #If we've gone past the left edge of the screen...
            self.state = UFO.STATES.LEAVING

    def die(self):
        '''
        Vanish and release a special Block that clears lots of other Blocks.
        '''
        UFO.BLOCK_GROUP.add(get_block([self.rect.centerx, 0], special=True))
        self.state = UFO.STATES.LEAVING

    def leave(self):
        UFO.invade.stop()
        self.velocity[0]  = 0
        self.position     = list(START_POS)
        self.rect.topleft = START_POS
        self.state        = UFO.STATES.IDLE

    def wait(self):
        '''
        Wait off-screen, and only come back with a specific probability.
        '''
        if uniform(0, 1) < self.odds:
        #With a certain probability...
            self.state = UFO.STATES.APPEARING

    actions = {
                STATES.IDLE     : 'wait'  ,
                STATES.APPEARING: 'appear',
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.LEAVING  : 'leave' ,
              }