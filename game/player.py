import pygame.key
import pygame.rect

import core.color  as color
import core.config as config

import gameobject
import ingame
import shipbullet

'''The Ship is the player character.  There's only going to be one instance of
it, but it has to inherit from pygame.sprite.Sprite, so I can't make it a true
Python singleton.
'''

#Constants/magic numbers#
STATES       = config.Enum('IDLE', 'SPAWNING', 'INVINCIBLE', 'ACTIVE', 'DYING', 'RESPAWN')
SURFACE_CLIP = pygame.Rect(0, 0, 32, 32)
START_POS    = pygame.Rect(config.screen.get_width() /  2,
                           config.screen.get_height()* .8,
                           32        ,
                           32)
SPEED        = 4
#########################

class Ship(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.mybullet        = shipbullet.ShipBullet()
        self.image           = config.SPRITES.subsurface(SURFACE_CLIP).copy() #@UndefinedVariable
        self.rect            = START_POS.copy()
        self.position        = list(self.rect.topleft)
        self.state           = STATES.ACTIVE
        self.invincible      = False
        self.invincibleCount = 0
        
        self.image.set_colorkey(color.COLOR_KEY)
        
    def on_fire_bullet(self):
        if self.mybullet.state == self.mybullet.__class__.STATES.IDLE:
        #If our bullet is not already on-screen...
            self.mybullet.add(ingame.PLAYER)
            self.mybullet.rect.midbottom = self.rect.midtop
            self.mybullet.position       = list(self.rect.midbottom)
            self.mybullet.state          = self.mybullet.__class__.STATES.FIRED
            
    def respawn(self):
        self.rect            = START_POS.copy()
        self.position        = list(self.rect.topleft)
        self.invincibleCount = 250
        self.invincible      = True
        self.state           = STATES.ACTIVE
        
    def move(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
        #If we're pressing left and not at the left edge of the screen...
            self.velocity[0] = -SPEED
        elif keys[pygame.K_RIGHT] and self.rect.right < config.screen.get_width():
        #If we're pressing right and not at the right edge of the screen...
            self.velocity[0] = SPEED
        else:
            self.velocity[0] = 0
            
        self.velocity[0] += self.acceleration[0]
        self.position[0] += self.velocity[0]
        self.rect.x       = self.position[0] + .5
        
        if self.invincibleCount == 0:
        #If we're no longer invincible...
            self.invincible = False
            self.image.set_alpha(255)
            
        else:
            self.invincibleCount -= 1
            self.image.set_alpha(128)
            
            
    def die(self):
        self.visible = False
        self.state   = STATES.IDLE
        
    actions = {
               STATES.IDLE      : None          ,
               STATES.SPAWNING  : 'respawn'       ,
               STATES.INVINCIBLE: NotImplemented,
               STATES.ACTIVE    : 'move'          ,
               STATES.DYING     : 'die'           ,
               STATES.RESPAWN   : 'respawn'
              }