import pygame
import enum
import config
import player

STATES       = enum.Enum('IDLE', 'FIRED', 'MOVING', 'COLLIDE', 'RESET')
SURFACE_CLIP = pygame.Rect(23, 5, 28, 10)
START_POS    = pygame.Rect(0, config.screen.get_height()*2, 0, 0)
SPEED        = 8


class ShipBullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = START_POS.copy()
        self.image = config.SPRITES.subsurface(SURFACE_CLIP) #@UndefinedVariable
        self.state = STATES.IDLE
        
        self.actions = {
                        STATES.IDLE   : lambda: None,
                        STATES.FIRED  : self.fire(),
                        STATES.MOVING : self.rect.move_ip(0, -SPEED),
                        STATES.COLLIDE: lambda: None,
                        STATES.RESET  : lambda: None,
                        }
        
    def update(self):
        try:
            self.actions[self.state]()
        except TypeError:
            pass
        
        if self.rect.bottom < 0:
            self.rect = START_POS
            self.state = STATES.IDLE  
            
    def fire(self):
        #Play a sound here later
        print("I'm going!")
        self.state = STATES.MOVING