'''
This is the bullet the enemy has available.  It is not meant to be created
and deleted over and over, but to be reused by the enemy (so we don't take as
much time creating and destroying bullets).
'''

from math import sin

import pygame.rect

from core        import config
from core        import color
from game.bullet import Bullet
from game.player import Ship
from game        import gamedata

### Constants ##################################################################
BULLET_STATES = ('IDLE', 'FIRED', 'MOVING', 'DYING', 'RESET')
################################################################################

### Globals ####################################################################
_enemy_bullets = set()
################################################################################

### Functions ##################################################################
def clean_up():
    '''
    Removes all EnemyBullets from memory.
    '''
    _enemy_bullets.clear()
    EnemyBullet.halt = False
    
def all_disappear():
    for i in EnemyBullet.GROUP:
        i.change_state(i.__class__.STATES.RESET)

def get_enemy_bullet():
    '''
    Retrieves a spare EnemyBullet, or creates one if there aren't any.
    '''
    if not _enemy_bullets:
    #If we don't have any spare EnemyBullets...
        _enemy_bullets.add(EnemyBullet())

    bullet = _enemy_bullets.pop()
    bullet.change_state(bullet.__class__.STATES.FIRED)
    return bullet

################################################################################

class EnemyBullet(Bullet):
    SPEED     = 2
    START_POS = pygame.Rect(30, config.screen.get_height() * 2, 5, 5)
    STATES    = config.Enum(*BULLET_STATES)
    FRAME     = pygame.Rect(262, 6, 20, 18)
    GROUP     = None
    halt      = False

    def __init__(self):
        super().__init__()
        self.blink_timer = 3 * 60
        self.image = config.SPRITES.subsurface(self.__class__.FRAME)
        self.image.set_colorkey(color.COLOR_KEY, config.BLIT_FLAGS)

    def move(self):
        '''
        Moves down the screen.
        '''
        super().move()

        if self.rect.top > config.SCREEN_HEIGHT:
        #If below the bottom of the screen...
            self.change_state(self.__class__.STATES.RESET)

    def reset(self):
        '''
        Remove this EnemyBullet from the game screen, but not from memory.
        '''
        super().reset()
        _enemy_bullets.add(self)
        self.blink_timer = 3 * 60
        
    def blink(self):
        self.blink_timer -= 1
        
        self.image.set_alpha(256 * (sin(self.blink_timer / 4) > 0))
            
        if not self.blink_timer:
        #If we're done animating...
            self.image.set_alpha(256)
            EnemyBullet.halt = False
            self.change_state(EnemyBullet.STATES.RESET)

    def kill_player(self, other):
        '''
        Kills the player.  Called if this EnemyBullet collides with the player.
        '''
        if not other.invincible and other.state == Ship.STATES.ACTIVE:
        #If the player is not invincible...
            gamedata.lives  -= 1
            all_disappear()
            EnemyBullet.halt = True
            other.change_state(Ship.STATES.DYING)
            self.change_state(self.__class__.STATES.DYING)
            
            
            
    actions  = {
                STATES.IDLE   : None          ,
                STATES.FIRED  : 'start_moving',
                STATES.MOVING : 'move'        ,
                STATES.DYING  : 'blink'       ,
                STATES.RESET  : 'reset'       ,
                }
    collisions = {Ship: kill_player}
