import random

import pygame

import gameobject
import block
from core import color
from core import config
import ingame

START_POS = (640, 16)
#The UFO's starting position; it waits here when idle.

class UFO(gameobject.GameObject):
    STATES = config.Enum('IDLE', 'APPEARING', 'ACTIVE', 'DYING', 'LEAVING')
    
    invade = pygame.mixer.Sound("./sfx/ufo.wav")
    #The sound the UFO makes as it flies across the screen
    
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.image    = config.SPRITES.subsurface(pygame.Rect(32, 64, 64, 32)).copy()
        #The UFO image; by default, the plain white one (it will be recolored)
        
        self.frames   = tuple(color.blend_color(self.image.copy(), c) for c in color.LIST[:config.NUM_COLORS])
        #The colors that the UFO cycles through
        
        self.rect     = pygame.Rect(START_POS, self.image.get_size())
        #The collision boundary of the USO
        
        self.position = list(START_POS)

        for c in self.frames:
        #For all colored UFO sprites...
            c.set_colorkey(c.get_at((0, 0)), config.FLAGS)
            
        self.state = UFO.STATES.IDLE
        
    def appear(self):
        self.velocity[0]  = -0.9
        self.rect.topleft = list(START_POS)
        self.position     = list(START_POS)
        self.state        = UFO.STATES.ACTIVE
    
    def move(self):
        #UFO.invade.play()
            
        self.position[0] += self.velocity[0]
        self.rect.left    = self.position[0] + .5
        self.image        = random.choice(self.frames)
        
        if self.rect.right < 0:
        #If we've gone past the left edge of the screen...
            self.state = UFO.STATES.LEAVING
        
    def die(self):
        ingame.BLOCKS.add(block.get_block([self.rect.centerx, 0], random.choice(color.LIST), special = True))
        self.state        = UFO.STATES.LEAVING
        
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