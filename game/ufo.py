import random

import pygame

import gameobject
import block
from core import color
from core import config
import ingame

STATES = config.Enum('IDLE', 'APPEARING', 'MOVING', 'DYING', 'LEAVING')
START_POS = (640, 16)

invade   = pygame.mixer.Sound("./sfx/ufo.wav")

class UFO(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.image    = config.SPRITES.subsurface(pygame.Rect(16*config.SCALE_FACTOR, 32*config.SCALE_FACTOR,
                                                              32*config.SCALE_FACTOR, 16*config.SCALE_FACTOR)).copy()
        self.frames   = tuple(color.blend_color(self.image.copy(), c) for c in color.Colors.LIST[:config.NUM_COLORS])
        self.rect     = pygame.Rect(START_POS, (self.image.get_width(), self.image.get_height()))
        self.position = list(START_POS)

        for c in self.frames:
            c.set_colorkey(c.get_at((0, 0)))
        self.state    = STATES.IDLE
        
    def appear(self):
        self.velocity[0]  = -.9
        self.rect.topleft = list(START_POS)
        self.position     = list(START_POS)
        #self.add(ingame.ENEMIES)
        self.state        = STATES.MOVING
    
    def move(self):
        invade.play()
            
        self.position[0] += self.velocity[0]
        self.rect.left   = self.position[0] + .5
        self.image       = random.choice(self.frames)
        
        if self.rect.right < 0:
        #If we've gone past the left edge of the screen...
            self.state = STATES.DYING
        
    def die(self):
        self.kill()
        ingame.BLOCKS.add(block.Block([self.rect.centerx, 0], random.choice(color.Colors.LIST), specialblock=True))
        invade.stop()
        self.velocity[0]  = 0
        self.position     = list(START_POS)
        self.rect.topleft = START_POS
        self.state        = STATES.IDLE
        
    actions = {
                STATES.IDLE     : None  ,
                STATES.APPEARING: appear,
                STATES.MOVING   : move  ,
                STATES.DYING    : die   ,
                STATES.LEAVING  : NotImplemented
              }