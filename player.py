import config
import pygame
import enum

SHIP_STATES = enum.Enum('SPAWNING', 'NORMAL', 'ACTION')

class Ship(pygame.sprite.Sprite):
    state = SHIP_STATES.SPAWNING
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.rect.Rect(32, 32, 32, 32)
        
        self.image = config.SPRITES
        self.image.set_clip(pygame.rect.Rect(0, 0, 16, 16))
        
    def update(self):
        if pygame.key.get_pressed()[pygame.K_LEFT] and self.rect.left >= 0:
            self.rect.move_ip(-4, 0)
        else:
            if pygame.key.get_pressed()[pygame.K_RIGHT] and \
                self.rect.right <= config.screen.get_width():
                    self.rect.move_ip(4, 0)