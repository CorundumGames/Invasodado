import pygame.key

import core.color  as color
import core.config as config

import gameobject
import ingame
import shipbullet

'''
The Ship is the player character.  There's only going to be one instance of
it, but it has to inherit from pygame.sprite.Sprite, so I can't make it a true
Python singleton.
'''

#Constants/magic numbers#
STATES    = config.Enum('IDLE', 'SPAWNING', 'INVINCIBLE', 'ACTIVE', 'DYING', 'DEAD', 'RESPAWN')
FRAMES    = [config.SPRITES.subsurface(pygame.Rect(32 * i, 128, 32, 32)).copy() for i in range(5)]
START_POS = pygame.Rect(config.screen.get_width() /  2,
                        config.screen.get_height()* .8,
                        32        ,
                        32)
SPEED     = 4
#########################

class Ship(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)
        
        self.anim            = 0.0
        self.mybullet        = shipbullet.ShipBullet()
        self.image           = FRAMES[0] #@UndefinedVariable
        self.rect            = START_POS.copy()
        self.position        = list(self.rect.topleft)
        self.state           = STATES.ACTIVE
        self.invincible      = False
        self.invincible_count = 0
        
        for i in FRAMES:
            i.set_colorkey(color.COLOR_KEY, config.FLAGS)
        
    def on_fire_bullet(self):
        bul = self.mybullet
        if bul.state == bul.__class__.STATES.IDLE and self.state == STATES.ACTIVE:
        #If our bullet is not already on-screen...
            self.anim = 1
            self.image = FRAMES[self.anim]
            bul.add(ingame.PLAYER)
            #bul.rect.midbottom = self.rect.midtop
            bul.rect.center = self.rect.center
            bul.position       = list(self.rect.midbottom)
            bul.state          = bul.__class__.STATES.FIRED
            
    def respawn(self):
        self.image.set_alpha(128)
        self.rect             = START_POS.copy()
        self.position         = list(self.rect.topleft)
        self.invincible_count = 250
        self.invincible       = True
        self.state            = STATES.ACTIVE
        
    def move(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        
        if self.state not in (STATES.DYING, STATES.DEAD, STATES.IDLE):
            if keys[pygame.K_LEFT] and self.rect.left > 0:
            #If we're pressing left and not at the left edge of the screen...
                self.velocity[0] = -SPEED
            elif keys[pygame.K_RIGHT] and self.rect.right < config.SCREEN_RECT.right:
            #If we're pressing right and not at the right edge of the screen...
                self.velocity[0] = SPEED
            else:
                self.velocity[0] = 0
            
        self.velocity[0] += self.acceleration[0]
        self.position[0] += self.velocity[0]
        self.rect.x       = self.position[0] + .5
        
        if self.invincible_count == 0:
        #If we're no longer invincible...
            self.invincible = False
            self.image.set_alpha(255)    
        else:
            self.invincible_count -= 1
            
        if 0 < self.anim < len(FRAMES) - 1:
            self.anim += 1.0/3.0
        else:
            self.anim  = 0
        self.image = FRAMES[int(self.anim)]
            
            
    def die(self):
        self.visible = False
        self.state   = STATES.RESPAWN
        
    actions = {
               STATES.IDLE      : None            ,
               STATES.SPAWNING  : 'respawn'       ,
               STATES.INVINCIBLE: None,
               STATES.ACTIVE    : 'move'          ,
               STATES.DYING     : 'die'           ,
               STATES.DEAD      : NotImplemented,
               STATES.RESPAWN   : 'respawn'
              }
    
class FlameTrail(gameobject.GameObject):
    pass