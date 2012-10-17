import pygame.sprite

from core import config
import gameobject

class HudObject(gameobject.GameObject):
    '''HudObject is meant for displays like lives, score, etc.
    It is its own type so it can be in collisions.do_not_check, because we
    don't intend for these to collide with anything.
    '''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.acceleration = None
        self.actions      = None
        self.position     = None
        self.rect         = None
        self.state        = None
        self.velocity     = None
        
    