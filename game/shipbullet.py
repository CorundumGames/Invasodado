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
'''
@var SHOOT: The sound that plays when the player fires
'''
SHOOT = config.load_sound('shoot.wav')
################################################################################

class ShipBullet(Bullet):
    SPEED     = -8
    START_POS = pygame.Rect(30, config.screen.get_height() * 2, 26, 19)
    GROUP     = None

    def __init__(self):
        super().__init__()
        self.column    = 0
        self.hit_enemy = False
        
    def start_moving(self):
        SHOOT.play()
        super().start_moving()
        self.column    = round(self.position[0] / 32)
        self.hit_enemy = False

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
        if not self.hit_enemy and other.state in {other.__class__.STATES.ACTIVE, other.__class__.STATES.LOWERING}:
        #If we hit another enemy that's alive...
            self.hit_enemy = True
            gamedata.score += 1
            self.change_state(self.__class__.STATES.RESET)
            other.change_state(other.__class__.STATES.DYING)
            other.column = self.column

    
    collisions = {
                  Enemy: kill_enemy,
                  UFO  : kill_enemy,
                 }