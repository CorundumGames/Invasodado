'''
This is the bullet the ship has available.  It is not meant to be created
and deleted over and over, but to be reused by the ship (so we don't take as
much time creating and destroying bullets).
'''
from os.path import join

import pygame.rect

from core        import config
from game.bullet import Bullet
from game.enemy  import Enemy
from game.ufo    import UFO
from game        import gamedata

### Constants ##################################################################
SHOOT = pygame.mixer.Sound(join('sfx', 'shoot.wav'))
################################################################################

class ShipBullet(Bullet):
    SPEED     = -8
    START_POS = pygame.Rect(30, config.screen.get_height() * 2, 26, 19)
    GROUP     = None

    def __init__(self):
        super().__init__()
        
    def start_moving(self):
        SHOOT.play()
        super().start_moving()  

    def move(self):
        '''
        Moves up the screen, seeing if it's hit an enemy or exited.
        '''
        super().move()

        if self.rect.bottom < 0:
        #If above the top of the screen...
            self.change_state(self.__class__.STATES.RESET)

    def kill_enemy(self, other):
        '''
        Kills whatever enemy we collided with.
        '''
        if other.state is other.__class__.STATES.ACTIVE:
        #And that other enemy is alive...
            gamedata.score += 1
            self.change_state(self.__class__.STATES.RESET)
            other.change_state(other.__class__.STATES.DYING)

    
    collisions = {
                  Enemy: kill_enemy,
                  UFO  : kill_enemy,
                  }