'''
Bullet is an abstract class which ShipBullet and EnemyBullet will inherit from.
Bullet should NOT be created in and of itself.
'''

import pygame

from core            import config
from core            import color
from game.gameobject import GameObject

### Constants ##################################################################
BULLET_STATES = ('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
################################################################################

class Bullet(GameObject):
    FRAME  = pygame.Rect(227, 6, 26, 19)
    STATES = config.Enum(*BULLET_STATES)
    SPRITE = config.get_sprite(FRAME)

    def __init__(self):
        super().__init__()
        self.image    = self.__class__.SPRITE #@UndefinedVariable
        self.rect     = self.__class__.START_POS.copy()
        self.position = list(self.rect.topleft)
        self.state    = self.__class__.STATES.IDLE

        self.image.set_colorkey(color.COLOR_KEY, config.BLIT_FLAGS)

    def start_moving(self):
        '''
        Begins moving.
        '''
        self.position    = list(self.rect.topleft)
        self.velocity[1] = self.__class__.SPEED
        self.change_state(self.__class__.STATES.MOVING)

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
        self.change_state(self.__class__.STATES.IDLE)

    actions  = {
                STATES.IDLE   : None          ,
                STATES.FIRED  : 'start_moving',
                STATES.MOVING : 'move'        ,
                STATES.RESET  : 'reset'       ,
               }