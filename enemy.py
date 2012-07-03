import enum
import pygame

import config

FRAMES = [pygame.Rect(0, 16, 16, 16), pygame.Rect(16, 16, 16, 16)]
START_POS = pygame.Rect(32, 32, 0, 0)
STATES = enum.Enum('APPEARING', 'LOWERING', 'ACTIVE', 'DYING', 'IDLE')

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = START_POS.copy()
        self.image = config.SPRITES.subsurface(FRAMES[0]) #@UndefinedVariable