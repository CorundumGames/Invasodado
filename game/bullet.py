'''
Bullet is an abstract class which ShipBullet and EnemyBullet will inherit from.
Bullet should NOT be created in and of itself.
'''

import pygame

from core import config
from core import color
from game.gameobject import GameObject

class Bullet(GameObject):
    FRAME  = pygame.Rect(227, 6, 26, 19)
    STATES = config.Enum('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
    SPRITE = config.SPRITES.subsurface(FRAME)

    def __init__(self):
        GameObject.__init__(self)
        self.image    = self.__class__.SPRITE #@UndefinedVariable
        self.rect     = self.__class__.START_POS.copy()
        self.position = list(self.rect.topleft)
        self.state    = self.__class__.STATES.IDLE

        self.image.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def start_moving(self):
        '''
        Plays a sound and begins moving.
        '''
        #TODO: Play a sound here later
        self.position    = list(self.rect.topleft)
        self.velocity[1] = self.__class__.SPEED
        self.state       = self.__class__.STATES.MOVING

    def move(self):
        '''
        Bullets only move vertically in Invasodado.
        '''
        self.position[1] += self.velocity[1]
        self.rect.top     = self.position[1] + .5

    def reset(self):
        '''
        Resets the bullet back to its initial position.
        '''
        self.kill()
        self.velocity[1] = 0
        self.rect        = self.__class__.START_POS.copy()
        self.position    = list(self.rect.topleft)
        self.state       = self.__class__.STATES.IDLE

    actions  = {
                STATES.IDLE   : None          ,
                STATES.FIRED  : 'start_moving',
                STATES.MOVING : 'move'        ,
                STATES.COLLIDE: NotImplemented,
                STATES.RESET  : 'reset'       ,
               }