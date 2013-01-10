import math
import random

import pygame

import gameobject
import block
from core import color
from core import config
import ingame

FRAMES    = [pygame.Rect(64 * (i % 4), 192 + 32*(i/4), 64, 32) for i in range(10, -1, -1)]
START_POS = (640, 16)
ufo_frames = config.get_colored_objects(FRAMES)

class UFO(gameobject.GameObject):
    STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'DYING', 'LEAVING')
    
    invade = pygame.mixer.Sound("./sfx/ufo.wav")
    #The sound the UFO makes as it flies across the screen
    
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.anim     = 0.0
        
        self.image    = config.SPRITES.subsurface(FRAMES[0]).copy()
        #The UFO image; by default, the plain white one (it will be recolored)
        
        self.rect     = pygame.Rect(START_POS, self.image.get_size())
        #The collision boundary of the UFO
        
        self.position = list(START_POS)
            
        self.state = UFO.STATES.IDLE
        
    def appear(self):
        self.velocity[0]  = -1.1
        self.rect.topleft = list(START_POS)
        self.position     = list(START_POS)
        self.state        = UFO.STATES.ACTIVE
    
    def move(self):
        #UFO.invade.play()
        self.anim        += 1.0/2
        self.image        = ufo_frames[id(random.choice(color.LIST))][int(self.anim) % len(FRAMES)]
        self.position[0] += self.velocity[0]
        self.position[1] += math.sin(self.anim/4)
        self.rect.topleft    = (self.position[0] + .5, self.position[1] + .5)
        
        
        if self.rect.right < 0:
        #If we've gone past the left edge of the screen...
            self.state = UFO.STATES.LEAVING
        
    def die(self):
        ingame.BLOCKS.add(block.get_block([self.rect.centerx, 0], special = True))
        self.state = UFO.STATES.LEAVING
        
    def leave(self):
        self.kill()
        UFO.invade.stop()
        self.velocity[0]  = 0
        self.position     = list(START_POS)
        self.rect.topleft = START_POS
        self.state        = UFO.STATES.IDLE
        
    actions = {
                STATES.IDLE     : None    ,
                STATES.APPEARING: 'appear',
                STATES.ACTIVE   : 'move'  ,
                STATES.DYING    : 'die'   ,
                STATES.LEAVING  : 'leave' ,
              }