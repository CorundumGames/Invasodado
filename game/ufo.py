import math
import os.path
import random

import pygame

from core import color
from core import config
from game import block

from game.gameobject import GameObject

FRAMES    = [pygame.Rect(64 * (i % 4), 192 + 32*(i/4), 64, 32) for i in range(10, -1, -1)]
START_POS = (640, 16)
ufo_frames = color.get_colored_objects(FRAMES)

class UFO(GameObject):
    STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'DYING', 'LEAVING')
    invade = pygame.mixer.Sound(os.path.join('sfx', 'ufo.wav'))
    ufo_group = None
    block_group = None
    #The sound the UFO makes as it flies across the screen

    def __init__(self):
        GameObject.__init__(self)
        self.anim     = 0.0
        self.image    = config.SPRITES.subsurface(FRAMES[0]).copy()
        self.odds     = .0001
        self.position = list(START_POS)
        self.rect     = pygame.Rect(START_POS, self.image.get_size())
        self.state    = UFO.STATES.IDLE

        del self.acceleration

    def appear(self):
        self.position     = list(START_POS)
        self.rect.topleft = list(START_POS)
        self.state        = UFO.STATES.ACTIVE
        self.velocity[0]  = -1.1

    def move(self):
        p = self.position
        r = self.rect

        #UFO.invade.play()
        self.anim        += 0.5
        self.image        = ufo_frames[id(random.choice(color.LIST))][int(self.anim) % len(FRAMES)]
        p[0] += self.velocity[0]
        p[1] += math.sin(self.anim/4)
        r.topleft = (p[0] + .5, p[1] + .5)

        if r.right < 0:
        #If we've gone past the left edge of the screen...
            self.state = UFO.STATES.LEAVING

    def die(self):
        UFO.block_group.add(block.get_block([self.rect.centerx, 0], special = True))
        self.state = UFO.STATES.LEAVING

    def leave(self):
        UFO.invade.stop()
        self.velocity[0]  = 0
        self.position     = list(START_POS)
        self.rect.topleft = START_POS
        self.state        = UFO.STATES.IDLE

    def wait(self):
        if random.uniform(0, 1) < self.odds:
            self.state = UFO.STATES.APPEARING

    actions = {
                STATES.IDLE     : 'wait'  ,
                STATES.APPEARING: 'appear',
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.LEAVING  : 'leave' ,
              }