from config import pygame, enum

SHIP_STATES = enum.Enum('SPAWNING', 'NORMAL', 'ACTION')


class Ship(pygame.sprite.Sprite):
    state = SHIP_STATES.SPAWNING
    
    def __init__(self):
        self.image = pygame.image.load("")
    
    def update(self):
        