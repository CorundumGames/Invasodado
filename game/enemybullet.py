import pygame.rect

from core import config
from game.bullet import Bullet
from game import player
from game import gamedata

'''
This is the bullet the enemy has available.  It is not meant to be created
and deleted over and over, but to be reused by the enemy (so we don't take as
much time creating and destroying bullets).
'''

enemy_bullets = set()

def clean_up():
    enemy_bullets.clear()

def get_enemy_bullet():
    if len(enemy_bullets) == 0:
        enemy_bullets.add(EnemyBullet())

    b       = enemy_bullets.pop()
    b.state = b.__class__.STATES.FIRED
    return b


class EnemyBullet(Bullet):

    SPEED     = 2
    START_POS = pygame.Rect(30, config.screen.get_height()*2, 5, 5)
    FRAME     = pygame.Rect(262, 6, 20, 18)
    group     = None

    def __init__(self):
        from core import color
        super(self.__class__, self).__init__()
        self.image = config.SPRITES.subsurface(self.__class__.FRAME)
        self.image.set_colorkey(color.COLOR_KEY, config.FLAGS)

    def move(self):
        '''Moves down the screen'''
        super(self.__class__, self).move()

        if self.rect.top > config.SCREEN_HEIGHT:
        #If below the bottom of the screen...
            self.state = self.__class__.STATES.RESET

    def reset(self):
        super(self.__class__, self).reset()
        enemy_bullets.add(self)

    def kill_player(self, other):
        if not other.invincible and other.state is other.__class__.STATES.ACTIVE:
        #If the player is not invincible...
            gamedata.lives -= 1
            other.state   = other.__class__.STATES.DYING
            self.state    = self.__class__.STATES.RESET

    collisions = {player.Ship: kill_player}
