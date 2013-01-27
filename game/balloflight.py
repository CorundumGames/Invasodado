import random

import pygame

import core.color  as color
import core.config as config

import block
from gameobject import GameObject
import ingame

FRAMES       = [pygame.Rect(32 * i, 96, 32, 32) for i in range(5)]
TIME_TO_MOVE = 30 #In frames; remember, our target is 60FPS

ball_frames = config.get_colored_objects(FRAMES)

balls = set()

def clean_up():
    balls.clear()

def get_ball(startpos, color):
    if len(balls) == 0:
        balls.add(BallOfLight())

    b          = balls.pop()  #Teehee
    b.color    = color
    b.startpos = tuple(startpos)
    b.state    = BallOfLight.STATES.APPEARING
    return b

class BallOfLight(GameObject):
    collisions = None
    STATES     = config.Enum('IDLE', 'APPEARING', 'MOVING', 'DYING', 'RESET')

    def __init__(self, startpos = (-300, -300), color = random.choice(color.LIST)):
        GameObject.__init__(self)

        self.anim     = 0
        self.color    = color
        self.image    = ball_frames[id(color)][0]
        size = self.image.get_size()
        self.rect     = pygame.Rect(startpos, size)
        self.position = list(startpos)
        self.progress = 0.0
        self.target   = (round(startpos[0]/size[0])*size[1], 8.0)
        self.startpos = startpos
        self.state    = BallOfLight.STATES.IDLE

        del self.acceleration, self.velocity

    def appear(self):
        self.image        = ball_frames[id(self.color)][0]
        self.position     = list(self.startpos)
        self.progress     = 0.0
        self.rect.topleft = self.startpos
        self.state        = BallOfLight.STATES.MOVING
        self.target       = (round(self.position[0]/self.image.get_width())*self.image.get_height(), 8.0)
        assert config.SCREEN_RECT.collidepoint(self.target), \
        "BallOfLight's target should be on-screen, instead it's %s" % self.target

    def move(self):
        p = self.position
        s = self.startpos

        self.progress += 1
        percent        = self.progress/TIME_TO_MOVE
        target         = self.target

        if self.anim < len(FRAMES) - 1:
            self.anim += 1
            self.image = ball_frames[id(self.color)][self.anim]

        dx                = (percent**2)*(3-2*percent)
        ddx               = 1 - dx
        p[0]              = (s[0] * dx ) + (target[0] * ddx)
        p[1]              = (s[1] * ddx) + (target[1] * dx )
        self.rect.topleft = (p[0] + .5, p[1] + .5)

        if p[1] == target[1]:
            self.state = BallOfLight.STATES.DYING

    def vanish(self):
        balls.add(self)
        ingame.BLOCKS.add(block.get_block([self.rect.centerx, 0], self.color))
        self.remove(ingame.ENEMIES)
        self.anim         = 0
        self.position     = [-300, -300]
        self.rect.topleft = self.position
        self.state        = BallOfLight.STATES.IDLE

    actions = {
                STATES.IDLE     : None    ,
                STATES.APPEARING: 'appear',
                STATES.MOVING   : 'move'  ,
                STATES.DYING    : 'vanish',
                }