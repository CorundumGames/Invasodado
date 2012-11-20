import pygame.rect

import core.config as config
import bullet
import ingame
import player

'''This is the bullet the enemy has available.  It is not meant to be created
and deleted over and over, but to be reused by the enemy (so we don't take as
much time creating and destroying bullets).'''

class EnemyBullet(bullet.Bullet):
    SPEED        = 2
    START_POS    = pygame.Rect(30, config.screen.get_height()*2, 5, 5)
    
    def __init__(self):
        super(EnemyBullet, self).__init__()
        self.collisions = {
                           player.Ship: None
                           }
        self.add(ingame.ENEMIES)
    
    def on_collide(self, other):
        if isinstance(other, player.Ship):
        #If we hit the player...
            if not other.invincible:
            #If he's not invincible...
                ingame.lives -= 1
                other.state = player.STATES.RESPAWN
            self.state = self.__class__.STATES.RESET   
        
    def move(self):
        '''Moves up the screen, seeing if it's hit an enemy or exited.'''
        super(EnemyBullet, self).move()
        
        if self.rect.top > config.SCREEN_HEIGHT:
        #If below the bottom of the screen...
            self.state = self.__class__.STATES.RESET