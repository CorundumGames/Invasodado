import config
import pygame
import enum
import shipbullet
import gsm

'''The Ship is the player character.  There's only going to be one instance of
it, but it has to inherit from pygame.sprite.Sprite, so I can't make it a true
Python singleton.
'''

#Constants/magic numbers
STATES = enum.Enum('SPAWNING', 'NORMAL', 'ACTION')
SURFACE_CLIP = pygame.Rect(0, 0, 16, 16)
START_POS = pygame.Rect(config.screen.get_width()/2,
                        config.screen.get_height()*.8,
                        0,
                        0)
SPEED = 4
########################

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = config.SPRITES.subsurface(SURFACE_CLIP) #@UndefinedVariable
        self.image.set_colorkey(config.COLOR_KEY)
        self.rect = START_POS.copy()
        self.state = STATES.SPAWNING
        self.bullet = shipbullet.ShipBullet()
        
        
        
    def update(self):
        #Shorthand for which keys have been pressed
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-SPEED, 0)
        elif keys[pygame.K_RIGHT]:
            self.rect.move_ip(SPEED, 0)
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if self.bullet.state == shipbullet.STATES.IDLE:
                    self.bullet.add(gsm.current_state.group_list[0])
                    self.bullet.rect = pygame.Rect(self.rect.copy().midtop, (0, 0))
                    self.bullet.state = shipbullet.STATES.FIRED
                
            
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > config.screen.get_width():
            self.rect.right = config.screen.get_width()   