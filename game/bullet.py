import pygame

import core.config as config
import gameobject

'''Bullet is an abstract class which ShipBullet and EnemyBullet will inherit
from.  Bullet should NOT be created in and of itself.'''

class Bullet(gameobject.GameObject):
    FRAME        = pygame.Rect(23*config.SCALE_FACTOR, 5*config.SCALE_FACTOR, 5*config.SCALE_FACTOR, 5*config.SCALE_FACTOR)
    STATES       = config.Enum('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
    
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.image    = config.SPRITES.subsurface(self.__class__.FRAME) #@UndefinedVariable
        self.rect     = self.__class__.START_POS.copy()
        self.state    = self.__class__.STATES.IDLE
        
    def start_moving(self):
        '''Plays a sound and begins moving.'''
        #Play a sound here later
        self.position    = list(self.rect.topleft)
        self.velocity[1] = self.__class__.SPEED
        self.state       = self.__class__.STATES.MOVING
        
    def move(self):
        self.velocity[1] += self.acceleration[1]
        self.position[1] += self.velocity[1]
        self.rect.topleft = (self.position[0] + .5, self.position[1] + .5)
        
    def reset(self):
        '''Resets the bullet back to its initial position.'''
        self.kill()
        self.velocity[1] = 0
        self.rect        = self.__class__.START_POS.copy()
        self.position    = self.rect.topleft
        self.state       = self.__class__.STATES.IDLE
        
    actions  = {
                STATES.IDLE   : None          ,
                STATES.FIRED  : start_moving  ,
                STATES.MOVING : move          ,
                STATES.COLLIDE: NotImplemented,
                STATES.RESET  : reset         ,
               }