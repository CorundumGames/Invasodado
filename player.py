import config
import pygame
import shipbullet
import gsm
import gameobject

'''The Ship is the player character.  There's only going to be one instance of
it, but it has to inherit from pygame.sprite.Sprite, so I can't make it a true
Python singleton.
'''

#Constants/magic numbers#

STATES = config.Enum('SPAWNING', 'NORMAL', 'ACTION')
SURFACE_CLIP = pygame.Rect(0, 0, 16, 16)
START_POS = pygame.Rect(config.screen.get_width()/2,
                        config.screen.get_height()*.8,
                        16,  #The 16s are so we can use rect.right (but 0, 0
                        16)  #would be fine, too).
SPEED = 4
#########################

class Ship(gameobject.GameObject):
    def __init__(self):
        gameobject.GameObject.__init__(self)
        self.image = config.SPRITES.subsurface(SURFACE_CLIP) #@UndefinedVariable

        self.rect = START_POS.copy()
        self.state = STATES.SPAWNING
        self.bullet = shipbullet.ShipBullet()
        
        self.image.set_colorkey(config.COLOR_KEY)
        
    def update(self):
        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]
        self.rect.move_ip(self.velocity[0], self.velocity[1])
        
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.velocity[0] = -SPEED
        elif keys[pygame.K_RIGHT] and self.rect.right < config.screen.get_width():
            self.velocity[0] = SPEED
        else:
            self.velocity[0] = 0
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if self.bullet.state == shipbullet.STATES.IDLE:
                    self.bullet.add(gsm.current_state.group_list[0])
                    self.bullet.rect.midbottom = self.rect.copy().midtop
                    self.bullet.state = shipbullet.STATES.FIRED
            
            