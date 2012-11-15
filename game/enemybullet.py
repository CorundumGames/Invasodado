import pygame.rect

from core import config
import enemy
import gameobject
import ingame
import player

'''This is the bullet the enemy has available.  It is not meant to be created
and deleted over and over, but to be reused by the enemy (so we don't take as
much time creating and destroying bullets).'''

STATES       = config.Enum('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
FRAME        = pygame.Rect(23*config.SCALE_FACTOR, 5*config.SCALE_FACTOR, 5*config.SCALE_FACTOR, 5*config.SCALE_FACTOR)
START_POS    = pygame.Rect(30, config.screen.get_height()*2, 5, 5)
SPEED        = 2

class EnemyBullet(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)

        self.actions  = {
                         STATES.IDLE   : None             ,
                         STATES.FIRED  : self.start_moving,
                         STATES.MOVING : self.move        ,
                         STATES.COLLIDE: NotImplemented   ,
                         STATES.RESET  : self.reset       ,
                         }
        self.image    = config.SPRITES.subsurface(FRAME) #@UndefinedVariable
        self.rect     = START_POS.copy()
        self.state    = STATES.IDLE
        self.add(ingame.ENEMIES)
    
    def on_collide(self, other):
        if isinstance(other, player.Ship):
            if not other.invincible:
                ingame.lives -= 1
                other.state = player.STATES.RESPAWN
            self.state = STATES.RESET
            
    def start_moving(self):
        '''Plays a sound and begins moving.'''
        #Play a sound here later
        self.position    = list(self.rect.topleft)
        self.velocity[1] = SPEED
        self.state       = STATES.MOVING
        
    def move(self):
        '''Moves up the screen, seeing if it's hit an enemy or exited.'''
        self.velocity[1] += self.acceleration[1]
        self.position[1] += self.velocity[1]
        self.rect.topleft = map(round, self.position)
        
        
        if self.rect.bottom > config.SCREEN_HEIGHT:
        #If above the top of the screen...
            self.state = STATES.RESET
        
    def reset(self):
        '''Resets the bullet back to its initial position.'''
        self.kill()
        self.velocity[1] = 0
        self.rect        = START_POS.copy()
        self.state       = STATES.IDLE  