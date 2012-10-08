import pygame.key
import pygame.rect
import pygame.mouse

from core import color
from core import config
import gameobject
import ingame
import shipbullet

'''The Ship is the player character.  There's only going to be one instance of
it, but it has to inherit from pygame.sprite.Sprite, so I can't make it a true
Python singleton.
'''

#Constants/magic numbers#
STATES       = config.Enum('IDLE', 'SPAWNING', 'INVINCIBLE', 'ACTIVE')
SURFACE_CLIP = pygame.Rect(0, 0, 16*config.SCALE_FACTOR, 16*config.SCALE_FACTOR)
START_POS    = pygame.Rect(config.screen.get_width() /  2,
                           config.screen.get_height()* .8,
                           16*config.SCALE_FACTOR        ,
                           16*config.SCALE_FACTOR)
SPEED        = 4
#########################

class Ship(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.actions = {
                        STATES.IDLE      : None          ,
                        STATES.SPAWNING  : NotImplemented,
                        STATES.INVINCIBLE: NotImplemented,
                        STATES.ACTIVE    : self.move
                        }
        self.bullet   = shipbullet.ShipBullet()
        self.image    = config.SPRITES.subsurface(SURFACE_CLIP) #@UndefinedVariable
        self.rect     = START_POS.copy()
        self.position = list(self.rect.topleft)
        self.state    = STATES.ACTIVE
        
        self.image.set_colorkey(color.COLOR_KEY)
        
    def on_fire_bullet(self):
        if self.bullet.state == shipbullet.STATES.IDLE:
            self.bullet.add(ingame.PLAYER)
            self.bullet.rect.midbottom = self.rect.midtop
            self.bullet.state          = shipbullet.STATES.FIRED
        
    def move(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.velocity[0] = -SPEED
        elif keys[pygame.K_RIGHT] and self.rect.right < config.screen.get_width():
            self.velocity[0] = SPEED
        else:
            self.velocity[0] = 0
            
        self.velocity[0] += self.acceleration[0]
        self.position[0] += self.velocity[0]
        self.rect.x = round(self.position[0])