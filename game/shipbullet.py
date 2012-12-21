import pygame.rect

import core.config as config


import bullet
import enemy
import ingame
import ufo

'''
This is the bullet the ship has available.  It is not meant to be created
and deleted over and over, but to be reused by the ship (so we don't take as
much time creating and destroying bullets).
'''

class ShipBullet(bullet.Bullet):
    SPEED     = -8
    START_POS = pygame.Rect(30, config.screen.get_height()*2, 10, 10)
    
    def __init__(self):
        super(self.__class__, self).__init__()
        self.add(ingame.PLAYER)
        
    def move(self):
        '''Moves up the screen, seeing if it's hit an enemy or exited.'''
        super(self.__class__, self).move()
        
        if self.rect.bottom < 0:
        #If above the top of the screen...
            self.state = self.__class__.STATES.RESET
            
    def kill_enemy(self, other):
        if other.state == other.__class__.STATES.ACTIVE:
        #And that other enemy is alive...
            self.state  = self.__class__.STATES.RESET
            other.state = other.__class__.STATES.DYING
    
    collisions = {
                  enemy.Enemy: kill_enemy,
                  ufo.UFO    : kill_enemy 
                  }