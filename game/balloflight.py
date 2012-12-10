import random

import pygame

import core.color  as color
import core.config as config

import block
import gameobject
import ingame

FRAME        = pygame.Rect(0, 96, 32, 32)
TIME_TO_MOVE = 30 #In frames; remember, our target is 60FPS

ball_frames = dict([(id(c), color.blend_color(config.SPRITES.subsurface(FRAME).copy(), c)) for c in color.LIST])

global balls
balls = set()

def get_ball(thestartpos, thecolor):
    global balls
    if len(balls) == 0:
        print "france"
        balls.add(BallOfLight())
        
    b          = balls.pop()
    b.color    = thecolor
    b.startpos = tuple(thestartpos)
    b.state    = BallOfLight.STATES.APPEARING
    return b

class BallOfLight(gameobject.GameObject):
    collisions = None
    STATES     = config.Enum('IDLE', 'APPEARING', 'MOVING', 'DYING', 'RESET')
    
    def __init__(self, startpos = (0, 0), color = random.choice(color.LIST)):
        gameobject.GameObject.__init__(self)
        self.color    = color
        self.image    = ball_frames[id(self.color)]
        self.rect     = pygame.Rect(startpos, self.image.get_size())
        self.position = list(startpos)
        self.progress = 0.0
        self.target   = (round(self.position[0]/self.image.get_width())*self.image.get_height(), 8.0)
        self.startpos = startpos
        self.state    = self.__class__.STATES.IDLE
        
        self.acceleration = None
        self.velocity     = None
        
        
    def appear(self):
        self.image    = ball_frames[id(self.color)]
        self.image.set_colorkey(self.image.get_at((0, 0)), config.FLAGS)
        
        self.rect.topleft = self.startpos
        self.position     = list(self.startpos)
        self.progress     = 0.0
        self.target       = (round(self.position[0]/self.image.get_width())*self.image.get_height(), 8.0)
        self.state        = self.__class__.STATES.MOVING

        
    def move(self):
        self.progress += 1
        percent        = self.progress/TIME_TO_MOVE
        target         = self.target
        
        dx = (percent**2)*(3-2*percent)
        ddx = 1 - dx
        self.position[0]  = (self.startpos[0] * dx ) + (target[0] * ddx)
        self.position[1]  = (self.startpos[1] * ddx) + (target[1] * dx )
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        
        if self.position[1] == target[1]:
            self.state = self.__class__.STATES.DYING
            
    def vanish(self):
        global balls
        balls.add(self)
        ingame.BLOCKS.add(block.Block([self.rect.centerx, 0], self.color))
        self.remove(ingame.ENEMIES)
        self.position = [-300, -300]
        self.rect.topleft = self.position
        
        self.state = self.__class__.STATES.IDLE
        
    actions = {
                STATES.IDLE     : None  ,
                STATES.APPEARING: 'appear',
                STATES.MOVING   : 'move'  ,
                STATES.DYING    : 'vanish',
                }