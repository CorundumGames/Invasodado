'''
This is the bullet the enemy has available.  It is not meant to be created
and deleted over and over, but to be reused by the enemy (so we don't take as
much time creating and destroying bullets).
'''

import pygame.rect

from core        import config
from core        import color
from game.bullet import Bullet
from game.player import Ship
from game        import gamedata

_enemy_bullets = set()

def clean_up():
    '''
    Removes all EnemyBullets from memory.
    '''
    _enemy_bullets.clear()

def get_enemy_bullet():
    '''
    Retrieves a spare EnemyBullet, or creates one if there aren't any.
    '''
    if not _enemy_bullets:
    #If we don't have any spare EnemyBullets...
        _enemy_bullets.add(EnemyBullet())

    bullet       = _enemy_bullets.pop()
    bullet.state = bullet.__class__.STATES.FIRED
    return bullet


class EnemyBullet(Bullet):
    SPEED     = 2
    START_POS = pygame.Rect(30, config.screen.get_height() * 2, 5, 5)
    FRAME     = pygame.Rect(262, 6, 20, 18)
    GROUP     = None

    def __init__(self):
        super(self.__class__, self).__init__()
        self.image = config.SPRITES.subsurface(self.__class__.FRAME)
        self.image.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def move(self):
        '''
        Moves down the screen.
        '''
        super(self.__class__, self).move()

        if self.rect.top > config.SCREEN_HEIGHT:
        #If below the bottom of the screen...
            self.state = self.__class__.STATES.RESET

    def reset(self):
        '''
        Remove this EnemyBullet from the game screen, but not from memory.
        '''
        super(self.__class__, self).reset()
        _enemy_bullets.add(self)

    def kill_player(self, other):
        '''
        Kills the player.  Called if this EnemyBullet collides with the player.
        '''
        if not other.invincible and other.state == Ship.STATES.ACTIVE:
        #If the player is not invincible...
            gamedata.lives -= 1
            other.state     = Ship.STATES.DYING
            self.state      = self.__class__.STATES.RESET

    collisions = {Ship: kill_player}
